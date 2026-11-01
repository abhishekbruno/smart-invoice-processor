import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from config.settings import settings
from core.database import db
from utils.logger import logger

# Strict read-only scope for invoice attachment collection
GMAIL_SCOPES: List[str] = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailAuthService:
    """Manages Google OAuth 2.0 authentication for the Gmail RPA automation module."""

    def __init__(
        self,
        credentials_file: Optional[Path] = None,
        token_file: Optional[Path] = None,
        scopes: Optional[List[str]] = None,
    ):
        self.credentials_file = credentials_file or settings.GMAIL_CREDENTIALS_FILE
        self.token_file = token_file or settings.GMAIL_TOKEN_FILE
        self.scopes = scopes or GMAIL_SCOPES
        self._service: Optional[Resource] = None

    @property
    def is_credentials_file_present(self) -> bool:
        """Returns True if the OAuth 2.0 client secrets file exists."""
        return self.credentials_file.exists() and self.credentials_file.is_file()

    @property
    def is_token_file_present(self) -> bool:
        """Returns True if a saved authorized user token file exists."""
        return self.token_file.exists() and self.token_file.is_file()

    def get_credentials(self) -> Optional[Credentials]:
        """
        Loads saved user credentials from token_file, automatically refreshing if expired.
        Returns valid Credentials or None.
        """
        creds: Optional[Credentials] = None

        if self.is_token_file_present:
            try:
                creds = Credentials.from_authorized_user_file(
                    str(self.token_file), self.scopes
                )
            except Exception as e:
                logger.warning(f"Error loading saved Gmail token: {e}")
                creds = None

        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Gmail access token expired. Refreshing token via Google OAuth...")
                creds.refresh(Request())
                self._save_token(creds)
                logger.info("Gmail access token refreshed successfully.")
            except Exception as e:
                logger.error(f"Failed to refresh Gmail token: {e}")
                return None

        if creds and creds.valid:
            return creds

        return None

    def _save_token(self, creds: Credentials) -> None:
        """Persists credentials securely to the local token file."""
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.token_file.write_text(creds.to_json(), encoding="utf-8")

    def is_authenticated(self) -> bool:
        """Checks if there are active, valid credentials available."""
        creds = self.get_credentials()
        return creds is not None and creds.valid

    def get_service(self) -> Optional[Resource]:
        """Returns an authorized Google API client Resource for Gmail v1, or None."""
        creds = self.get_credentials()
        if not creds:
            return None

        try:
            # Reuse or build service
            self._service = build("gmail", "v1", credentials=creds, cache_discovery=False)
            return self._service
        except Exception as e:
            logger.error(f"Failed to initialize Gmail API client: {e}")
            return None

    def authenticate_desktop_flow(self, port: int = 0) -> Tuple[bool, str]:
        """
        Launches local desktop browser OAuth 2.0 flow using client secrets file.
        Saves resulting token to token_file and records account in SQLite.
        """
        if not self.is_credentials_file_present:
            msg = (
                f"OAuth credentials file not found at '{self.credentials_file}'. "
                "Download your OAuth 2.0 Client ID (Desktop app) credentials from Google Cloud Console "
                "and save it to config/credentials.json."
            )
            logger.warning(msg)
            return False, msg

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_file), self.scopes
            )
            creds = flow.run_local_server(
                port=port,
                prompt="consent",
                success_message="Authentication successful! You can close this window and return to the Smart Invoice Processor.",
            )
            self._save_token(creds)

            # Retrieve connected profile to record active email
            profile = self.get_user_profile(credentials=creds)
            email = profile.get("emailAddress", "connected_user@gmail.com") if profile else "connected_user@gmail.com"
            db.record_gmail_account(email)

            logger.info(f"Successfully authenticated Gmail account: {email}")
            return True, f"Successfully connected Gmail account: {email}"
        except Exception as e:
            err_msg = f"OAuth flow encountered an error: {str(e)}"
            logger.error(err_msg, exc_info=True)
            return False, err_msg

    def get_user_profile(self, credentials: Optional[Credentials] = None) -> Optional[Dict[str, Any]]:
        """Fetches the user's Gmail profile information (e.g., email address)."""
        creds = credentials or self.get_credentials()
        if not creds:
            return None

        try:
            service = build("gmail", "v1", credentials=creds, cache_discovery=False)
            profile = service.users().getProfile(userId="me").execute()
            return profile
        except Exception as e:
            logger.warning(f"Could not retrieve Gmail user profile: {e}")
            return None

    def disconnect(self) -> Tuple[bool, str]:
        """Safely disconnects Gmail by removing the local token file and deactivating the DB account."""
        self._service = None
        removed = False

        if self.token_file.exists():
            try:
                self.token_file.unlink()
                removed = True
                logger.info(f"Deleted saved Gmail token file: {self.token_file}")
            except Exception as e:
                logger.warning(f"Error removing token file: {e}")

        # Update database account status
        try:
            db.disconnect_gmail_account()
        except Exception as e:
            logger.warning(f"Error updating DB during Gmail disconnect: {e}")

        msg = "Gmail disconnected successfully. Local authentication credentials cleared."
        return True, msg

    def get_auth_status(self) -> Dict[str, Any]:
        """Returns structured diagnostic status of the Gmail OAuth integration."""
        creds_exist = self.is_credentials_file_present
        token_exist = self.is_token_file_present
        active_db_acc = db.get_active_gmail_account()

        is_auth = False
        token_expired = False
        connected_email = active_db_acc.get("email") if active_db_acc else None
        last_synced_at = active_db_acc.get("last_synced_at") if active_db_acc else None

        if token_exist:
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_file), self.scopes)
                if creds:
                    token_expired = creds.expired
                    is_auth = creds.valid or (creds.expired and bool(creds.refresh_token))
            except Exception:
                is_auth = False

        return {
            "is_configured": creds_exist,
            "is_authenticated": is_auth,
            "has_token": token_exist,
            "is_token_expired": token_expired,
            "connected_email": connected_email,
            "last_synced_at": last_synced_at,
            "credentials_path": str(self.credentials_file),
            "token_path": str(self.token_file),
            "scope": self.scopes[0],
        }


# Global singleton
gmail_auth_service = GmailAuthService()

