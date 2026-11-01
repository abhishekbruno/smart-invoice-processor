import io
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from google.oauth2.credentials import Credentials

from config.settings import settings
from core.database import db
from core.gmail_attachment_service import GmailAttachmentService
from core.gmail_auth_service import GmailAuthService
from core.gmail_service import GmailService
from core.gmail_sync_service import GmailSyncService


# =============================================================================
# 1. Gmail Auth Service Tests
# =============================================================================

def test_gmail_auth_missing_credentials_handling(tmp_path):
    """Verifies that missing credentials.json returns clear diagnostic status without crashing."""
    fake_creds = tmp_path / "non_existent_creds.json"
    fake_token = tmp_path / "non_existent_token.json"

    auth_svc = GmailAuthService(credentials_file=fake_creds, token_file=fake_token)
    assert not auth_svc.is_credentials_file_present
    assert not auth_svc.is_token_file_present
    assert not auth_svc.is_authenticated()

    ok, msg = auth_svc.authenticate_desktop_flow()
    assert not ok
    assert "OAuth credentials file not found" in msg

    status = auth_svc.get_auth_status()
    assert not status["is_configured"]
    assert not status["is_authenticated"]


def test_gmail_auth_saved_token_loading(tmp_path):
    """Verifies loading valid credentials from a saved token file."""
    token_file = tmp_path / "token.json"
    token_data = {
        "token": "fake_access_token",
        "refresh_token": "fake_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "fake_client_id.apps.googleusercontent.com",
        "client_secret": "fake_client_secret",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
        "expiry": "2099-01-01T00:00:00Z",
    }
    token_file.write_text(json.dumps(token_data))

    auth_svc = GmailAuthService(
        credentials_file=tmp_path / "creds.json",
        token_file=token_file,
    )
    assert auth_svc.is_token_file_present
    creds = auth_svc.get_credentials()
    assert creds is not None
    assert auth_svc.is_authenticated()


def test_gmail_auth_token_refresh_mock(tmp_path):
    """Verifies that expired credentials trigger token refresh."""
    token_file = tmp_path / "token.json"
    token_file.write_text(json.dumps({"token": "old_token"}))

    auth_svc = GmailAuthService(
        credentials_file=tmp_path / "creds.json",
        token_file=token_file,
    )

    mock_creds = MagicMock(spec=Credentials)
    mock_creds.expired = True
    mock_creds.refresh_token = "some_refresh_token"
    mock_creds.valid = True
    mock_creds.to_json.return_value = json.dumps({"token": "refreshed_token"})

    with patch("core.gmail_auth_service.Credentials.from_authorized_user_file", return_value=mock_creds):
        with patch.object(mock_creds, "refresh") as mock_refresh:
            creds = auth_svc.get_credentials()
            assert mock_refresh.called
            assert creds is mock_creds


def test_gmail_auth_disconnect(tmp_path):
    """Verifies that disconnecting removes the token file and clears DB status."""
    token_file = tmp_path / "token.json"
    token_file.write_text(json.dumps({"token": "to_be_deleted"}))

    auth_svc = GmailAuthService(
        credentials_file=tmp_path / "creds.json",
        token_file=token_file,
    )
    assert token_file.exists()

    db.record_gmail_account("test_user@gmail.com")
    active_acc = db.get_active_gmail_account()
    assert active_acc is not None
    assert active_acc["email"] == "test_user@gmail.com"

    ok, msg = auth_svc.disconnect()
    assert ok
    assert not token_file.exists()
    assert db.get_active_gmail_account() is None


# =============================================================================
# 2. Gmail Service Tests (Search, MIME Parsing & Downloading)
# =============================================================================

def test_gmail_search_messages_mock():
    """Tests message search with pagination handling."""
    mock_auth = MagicMock(spec=GmailAuthService)
    mock_service = MagicMock()
    mock_auth.get_service.return_value = mock_service

    # Page 1: returns msg1, msg2 with nextPageToken
    # Page 2: returns msg3 without nextPageToken
    page1 = {"messages": [{"id": "msg1", "threadId": "t1"}, {"id": "msg2", "threadId": "t2"}], "nextPageToken": "token2"}
    page2 = {"messages": [{"id": "msg3", "threadId": "t3"}]}

    mock_service.users().messages().list().execute.side_effect = [page1, page2]

    svc = GmailService(auth_service=mock_auth)
    results = svc.search_messages(query="has:attachment filename:pdf", max_results=10)
    assert len(results) == 3
    assert results[0]["id"] == "msg1"
    assert results[2]["id"] == "msg3"


def test_gmail_extract_headers():
    """Tests header extraction for From, Subject, Date, and Message-ID."""
    sample_payload = {
        "payload": {
            "headers": [
                {"name": "From", "value": "Billing <billing@aws.amazon.com>"},
                {"name": "Subject", "value": "Amazon Web Services Invoice INV-AWS-2024-8192"},
                {"name": "Date", "value": "Mon, 15 Jan 2024 10:00:00 +0000"},
                {"name": "To", "value": "accounting@company.com"},
            ]
        }
    }
    headers = GmailService.extract_headers(sample_payload)
    assert "billing@aws.amazon.com" in headers["from"]
    assert "INV-AWS-2024-8192" in headers["subject"]
    assert headers["date"] == "Mon, 15 Jan 2024 10:00:00 +0000"


def test_gmail_find_pdf_attachments_nested_mime():
    """Tests recursive discovery of PDF attachments in complex nested MIME multipart messages."""
    sample_message = {
        "payload": {
            "mimeType": "multipart/mixed",
            "parts": [
                {
                    "mimeType": "multipart/alternative",
                    "parts": [
                        {"mimeType": "text/plain", "body": {"size": 100}},
                        {"mimeType": "text/html", "body": {"size": 250}},
                    ],
                },
                {
                    "mimeType": "application/pdf",
                    "filename": "AWS_January_Invoice.pdf",
                    "body": {"attachmentId": "att_aws_12345", "size": 45000},
                },
                {
                    "mimeType": "image/png",
                    "filename": "logo.png",
                    "body": {"attachmentId": "att_img_999", "size": 12000},
                },
            ],
        }
    }
    svc = GmailService()
    attachments = svc.find_pdf_attachments(sample_message)
    assert len(attachments) == 1
    assert attachments[0]["attachment_id"] == "att_aws_12345"
    assert attachments[0]["filename"] == "AWS_January_Invoice.pdf"
    assert attachments[0]["size"] == 45000


def test_gmail_download_attachment_bytes_mock():
    """Tests downloading and decoding base64url attachment content."""
    mock_auth = MagicMock(spec=GmailAuthService)
    mock_service = MagicMock()
    mock_auth.get_service.return_value = mock_service

    # URL-safe base64 for b"%PDF-1.4 Mock Invoice Content"
    raw_b64 = "JVBERi0xLjQgTW9jayBJbnZvaWNlIENvbnRlbnQ="
    mock_service.users().messages().attachments().get().execute.return_value = {"data": raw_b64}

    svc = GmailService(auth_service=mock_auth)
    data = svc.download_attachment_bytes("msg123", "att456")
    assert data is not None
    assert data.startswith(b"%PDF-")


# =============================================================================
# 3. Gmail Attachment Service Tests (Validation, Stage 1 Deduplication)
# =============================================================================

def test_gmail_attachment_validation_rejects_non_pdf(tmp_path):
    """Verifies that attachments without %PDF- magic bytes are rejected."""
    att_svc = GmailAttachmentService(watch_dir=tmp_path)
    res = att_svc.process_attachment(
        content_bytes=b"NOT_A_PDF_DOCUMENT_CONTENT",
        filename="corrupted_file.pdf",
        attachment_id="att_invalid_1",
        message_id="msg_test_1",
    )
    assert res["status"] == "failed"
    assert "magic bytes" in res["error"]


def test_gmail_attachment_validation_rejects_empty(tmp_path):
    """Verifies that empty attachments (0 bytes) are rejected."""
    att_svc = GmailAttachmentService(watch_dir=tmp_path)
    res = att_svc.process_attachment(
        content_bytes=b"",
        filename="empty.pdf",
        attachment_id="att_empty_1",
        message_id="msg_test_2",
    )
    assert res["status"] == "failed"
    assert "empty" in res["error"]


def test_gmail_attachment_stage1_duplicate_skipping(tmp_path):
    """Verifies Stage 1 deduplication skips an attachment that was already downloaded/processed."""
    watch_dir = tmp_path / "invoices"
    att_svc = GmailAttachmentService(watch_dir=watch_dir)

    # Use a real valid sample PDF from data/samples/
    sample_pdf_path = settings.SAMPLES_DIR / "AWS_INV_2024_8192.pdf"
    assert sample_pdf_path.exists(), "Sample PDF must exist for attachment testing"
    sample_bytes = sample_pdf_path.read_bytes()

    # First attempt: should succeed or identify duplicate if hash is already in DB
    msg_id = "msg_unique_first_run"
    att_id = "att_unique_first_run"

    # Pre-record attachment in DB to test Stage 1 check directly
    db.record_processed_attachment(
        message_id=msg_id,
        attachment_id=att_id,
        file_name="AWS_INV_2024_8192.pdf",
        download_status="downloaded",
    )

    res = att_svc.process_attachment(
        content_bytes=sample_bytes,
        filename="AWS_INV_2024_8192.pdf",
        attachment_id=att_id,
        message_id=msg_id,
    )
    assert res["status"] == "skipped_duplicate"
    assert "already processed" in res["message"]


# =============================================================================
# 4. Gmail Sync Service Tests (End-to-End Mock Run)
# =============================================================================

def test_gmail_sync_service_unauthenticated_early_exit():
    """Verifies that run_sync returns an error when Gmail is not authenticated."""
    mock_auth = MagicMock(spec=GmailAuthService)
    mock_auth.is_authenticated.return_value = False

    sync_svc = GmailSyncService(auth_service=mock_auth)
    res = sync_svc.run_sync()
    assert res["status"] == "error"
    assert "not authenticated" in res["error"]


def test_gmail_sync_service_end_to_end_mock(tmp_path):
    """Tests a full simulated sync cycle with 2 messages and 1 valid PDF attachment."""
    mock_auth = MagicMock(spec=GmailAuthService)
    mock_auth.is_authenticated.return_value = True

    mock_api = MagicMock(spec=GmailService)
    mock_att = MagicMock(spec=GmailAttachmentService)

    # 1 message found
    mock_api.search_messages.return_value = [{"id": "msg_sync_1", "threadId": "t_sync_1"}]
    mock_api.get_message_details.return_value = {
        "id": "msg_sync_1",
        "payload": {
            "headers": [
                {"name": "From", "value": "Billing <billing@stripe.com>"},
                {"name": "Subject", "value": "Stripe Invoice #STR-9912"},
                {"name": "Date", "value": "2024-05-01"},
            ]
        },
    }
    mock_api.extract_headers.return_value = {
        "from": "billing@stripe.com",
        "subject": "Stripe Invoice #STR-9912",
        "date": "2024-05-01",
    }
    mock_api.find_pdf_attachments.return_value = [
        {"attachment_id": "att_stripe_1", "filename": "Stripe_Invoice.pdf", "size": 12000}
    ]
    mock_api.download_attachment_bytes.return_value = b"%PDF-1.4 Mock Stripe Content"

    mock_att.process_attachment.return_value = {
        "status": "success",
        "file_name": "gmail_msg_sy_Stripe_Invoice.pdf",
        "invoice_id": 999,
    }

    sync_svc = GmailSyncService(
        auth_service=mock_auth,
        api_service=mock_api,
        attachment_service=mock_att,
    )

    res = sync_svc.run_sync(query="has:attachment filename:pdf", max_messages=10)
    assert res["status"] == "success"
    assert res["messages_scanned"] == 1
    assert res["attachments_found"] == 1
    assert res["invoices_imported"] == 1
    assert res["duplicates_skipped"] == 0
    assert res["failed_count"] == 0


def test_gmail_background_sync_worker_lifecycle():
    """Tests starting and cleanly stopping the background sync daemon thread."""
    mock_auth = MagicMock(spec=GmailAuthService)
    mock_auth.is_authenticated.return_value = False  # Keep idle in loop

    sync_svc = GmailSyncService(auth_service=mock_auth)
    assert not sync_svc.is_background_sync_running

    sync_svc.start_background_sync(interval_minutes=60)
    assert sync_svc.is_background_sync_running

    # Starting a second time should not spawn multiple threads
    sync_svc.start_background_sync(interval_minutes=60)
    assert sync_svc.is_background_sync_running

    sync_svc.stop_background_sync()
    assert not sync_svc.is_background_sync_running
