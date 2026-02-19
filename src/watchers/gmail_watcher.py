"""
Gmail Watcher Implementation
Monitors Gmail inbox for new unread emails using the Gmail API (OAuth2).
Creates action files in Needs_Action/ for each new unread message.
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from watchers.base_watcher import BaseWatcher

logger = logging.getLogger(__name__)


class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, check_interval: int = 120):
        super().__init__(vault_path, check_interval)
        self.credentials_file = os.getenv(
            'GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json'
        )
        self.token_file = os.getenv('GMAIL_TOKEN_FILE', 'gmail_token.json')
        self._service = None
        self._seen_ids: set[str] = set()

    def _ensure_service(self):
        """Initialize Gmail API service with OAuth2 if not already started"""
        if self._service is not None:
            return

        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
        except ImportError:
            logger.error(
                "Google API libraries not installed. Run: "
                "pip install google-api-python-client google-auth-oauthlib"
            )
            return

        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        creds = None

        # Load existing token
        token_path = Path(self.token_file)
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                cred_path = Path(self.credentials_file)
                if not cred_path.exists():
                    logger.error(
                        f"Gmail credentials file not found: {self.credentials_file}. "
                        "Download OAuth client JSON from Google Cloud Console."
                    )
                    return
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(cred_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for future runs
            token_path.write_text(creds.to_json(), encoding='utf-8')

        self._service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API service initialized")

    def check_for_updates(self) -> list:
        """Check Gmail for unread messages in the inbox"""
        self._ensure_service()
        if self._service is None:
            return []

        unread = []
        try:
            results = self._service.users().messages().list(
                userId='me',
                q='is:unread in:inbox',
                maxResults=10,
            ).execute()

            messages = results.get('messages', [])
            for msg_ref in messages:
                msg_id = msg_ref['id']
                if msg_id in self._seen_ids:
                    continue

                # Fetch message metadata
                msg = self._service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date'],
                ).execute()

                headers = {
                    h['name']: h['value']
                    for h in msg.get('payload', {}).get('headers', [])
                }

                self._seen_ids.add(msg_id)
                unread.append({
                    'type': 'email_received',
                    'message_id': msg_id,
                    'from': headers.get('From', 'Unknown'),
                    'subject': headers.get('Subject', '(no subject)'),
                    'date': headers.get('Date', ''),
                    'snippet': msg.get('snippet', ''),
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.error(f"Error checking Gmail: {e}")

        return unread

    def create_action_file(self, item) -> Path:
        """Create an action file for an unread Gmail message"""
        ts = int(datetime.now().timestamp())
        # Sanitize subject for filename
        safe_subject = "".join(
            c if c.isalnum() or c in '-_' else '_'
            for c in item['subject'][:40]
        )
        filename = f"gmail_{safe_subject}_{ts}.md"
        filepath = self.needs_action / filename

        content = f"""---
action_type: email_received
from: {item['from']}
subject: {item['subject']}
---
# Email Received: {item['subject']}

## Message Details
- **Source**: Gmail
- **From**: {item['from']}
- **Subject**: {item['subject']}
- **Date**: {item['date']}
- **Received**: {item['timestamp']}

## Preview
> {item['snippet']}

## Action Required
Review the email and determine appropriate response.

## Recommended Actions
- Reply to the sender if response is needed
- Forward to relevant team member if applicable
- Archive or label for future reference
- Create follow-up task if needed
"""
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created Gmail action file: {filepath.name}")
        return filepath

    def cleanup(self):
        """Clean up resources"""
        self._service = None


if __name__ == "__main__":
    from utils.logger import setup_logger
    from utils.config_loader import load_config

    config = load_config()
    setup_logger(config.get('LOG_LEVEL', 'INFO'))
    watcher = GmailWatcher(config['VAULT_PATH'])
    watcher.run()
