import base64
from typing import Any, Dict, List, Optional
from core.gmail_auth_service import GmailAuthService, gmail_auth_service
from utils.logger import logger


class GmailService:
    """Interacts with Gmail API to query messages, inspect MIME structures, and retrieve attachments."""

    def __init__(self, auth_service: Optional[GmailAuthService] = None):
        self.auth_service = auth_service or gmail_auth_service

    def search_messages(
        self,
        query: str = "has:attachment filename:pdf",
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Queries the user's Gmail mailbox using standard Gmail query syntax.
        Returns a list of message descriptors: [{'id': '...', 'threadId': '...'}, ...].
        """
        service = self.auth_service.get_service()
        if not service:
            logger.warning("Cannot search Gmail: Gmail service is not authenticated.")
            return []

        try:
            messages: List[Dict[str, Any]] = []
            page_token = None

            while True:
                req_kwargs: Dict[str, Any] = {
                    "userId": "me",
                    "q": query,
                    "maxResults": min(max_results - len(messages), 100),
                }
                if page_token:
                    req_kwargs["pageToken"] = page_token

                response = service.users().messages().list(**req_kwargs).execute()
                batch = response.get("messages", [])
                messages.extend(batch)

                page_token = response.get("nextPageToken")
                if not page_token or len(messages) >= max_results:
                    break

            logger.info(f"Gmail search query '{query}' matched {len(messages)} message(s).")
            return messages
        except Exception as e:
            logger.error(f"Error querying Gmail messages: {e}", exc_info=True)
            return []

    def get_message_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Fetches full payload and metadata for a specific message."""
        service = self.auth_service.get_service()
        if not service:
            return None

        try:
            return service.users().messages().get(userId="me", id=message_id, format="full").execute()
        except Exception as e:
            logger.error(f"Failed to fetch Gmail message #{message_id}: {e}")
            return None

    @staticmethod
    def extract_headers(message_data: Dict[str, Any]) -> Dict[str, str]:
        """Extracts standard email headers (From, Subject, Date, To) from message payload."""
        payload = message_data.get("payload", {})
        headers_list = payload.get("headers", [])
        parsed_headers: Dict[str, str] = {}

        target_headers = {"from", "subject", "date", "to", "message-id"}
        for h in headers_list:
            name = h.get("name", "").strip().lower()
            if name in target_headers:
                parsed_headers[name] = h.get("value", "")

        return {
            "from": parsed_headers.get("from", "Unknown Sender"),
            "subject": parsed_headers.get("subject", "(No Subject)"),
            "date": parsed_headers.get("date", ""),
            "to": parsed_headers.get("to", ""),
            "message_id_header": parsed_headers.get("message-id", ""),
        }

    def find_pdf_attachments(self, message_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recursively scans message MIME payload and subparts to discover PDF attachments.
        Returns a list of dicts: [{'attachment_id': ..., 'filename': ..., 'size': ..., 'mime_type': ...}].
        """
        payload = message_data.get("payload", {})
        attachments: List[Dict[str, Any]] = []

        def _scan_part(part: Dict[str, Any]) -> None:
            filename = part.get("filename", "").strip()
            mime_type = part.get("mimeType", "").lower()
            body = part.get("body", {})
            attachment_id = body.get("attachmentId")

            is_pdf = (
                filename.lower().endswith(".pdf")
                or mime_type == "application/pdf"
                or mime_type == "application/x-pdf"
            )

            if is_pdf and attachment_id:
                attachments.append(
                    {
                        "attachment_id": attachment_id,
                        "filename": filename or f"attachment_{attachment_id[:8]}.pdf",
                        "size": body.get("size", 0),
                        "mime_type": mime_type or "application/pdf",
                    }
                )

            # Recurse through nested multipart boundaries
            for subpart in part.get("parts", []):
                _scan_part(subpart)

        _scan_part(payload)
        return attachments

    def download_attachment_bytes(self, message_id: str, attachment_id: str) -> Optional[bytes]:
        """
        Retrieves the raw bytes of an attachment using Gmail API users.messages.attachments.get.
        Safely decodes URL-safe base64 payload.
        """
        service = self.auth_service.get_service()
        if not service:
            return None

        try:
            att_resp = (
                service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=message_id, id=attachment_id)
                .execute()
            )
            raw_data = att_resp.get("data", "")
            if not raw_data:
                return None

            # Add required base64 padding if missing
            padding = len(raw_data) % 4
            if padding:
                raw_data += "=" * (4 - padding)

            decoded_bytes = base64.urlsafe_b64decode(raw_data)
            return decoded_bytes
        except Exception as e:
            logger.error(f"Error downloading attachment {attachment_id} for message {message_id}: {e}")
            return None


# Global singleton
gmail_service = GmailService()

