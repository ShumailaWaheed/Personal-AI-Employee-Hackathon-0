"""
WhatsApp Watcher Implementation
Monitors WhatsApp Web for new messages using Playwright with persistent sessions
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from watchers.base_watcher import BaseWatcher

logger = logging.getLogger(__name__)


class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, check_interval: int = 30,
                 trigger_keywords: list[str] | None = None):
        super().__init__(vault_path, check_interval)
        self.playwright = None
        self.browser = None
        self.page = None
        self.session_dir = os.getenv('WHATSAPP_SESSION_DIR', './whatsapp_session')
        self._seen_ids: set[str] = set()
        self.trigger_keywords = [kw.lower() for kw in (trigger_keywords or ['urgent', 'bhai'])]

    def _ensure_browser(self):
        """Initialize Playwright browser with persistent context if not already started"""
        if self.page is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install")
            return

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.session_dir,
            headless=os.getenv('WHATSAPP_HEADLESS', 'false').lower() == 'true',
            viewport={'width': 1280, 'height': 800}
        )
        self.page = self.browser.new_page()
        self.page.goto("https://web.whatsapp.com/")
        logger.info("Waiting for WhatsApp Web login (scan QR if needed)...")
        self.page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
        logger.info("WhatsApp Web session ready")

    def _read_last_message(self, chat_element) -> str:
        """Click into a chat and read the last incoming message text"""
        try:
            chat_element.click()
            self.page.wait_for_selector('[data-testid="conversation-panel-messages"]', timeout=5000)
            # Get all incoming message rows (not outgoing)
            msg_rows = self.page.query_selector_all(
                '[data-testid="conversation-panel-messages"] [data-testid="msg-container"]'
            )
            if not msg_rows:
                return ""
            last_msg = msg_rows[-1]
            text_el = last_msg.query_selector('[data-testid="msg-text"] span.selectable-text')
            if text_el:
                return text_el.inner_text()
            # Fallback: try copyable-text span
            copyable = last_msg.query_selector('span.copyable-text')
            if copyable:
                return copyable.inner_text()
            return ""
        except Exception as e:
            logger.warning(f"Could not read last message: {e}")
            return ""

    def _contains_trigger_keyword(self, text: str) -> bool:
        """Check if text contains any trigger keyword (case-insensitive)"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.trigger_keywords)

    def check_for_updates(self) -> list:
        """Check WhatsApp Web for unread conversations with trigger keywords"""
        self._ensure_browser()
        if self.page is None:
            return []

        unread = []
        try:
            chat_elements = self.page.query_selector_all('[data-testid="cell-frame-container"]')
            for el in chat_elements:
                badge = el.query_selector('[data-testid="icon-unread-count"]')
                if not badge:
                    continue
                title_el = el.query_selector('span[title]')
                if not title_el:
                    continue
                contact = title_el.get_attribute('title')
                uid = f"wa_{contact}_{datetime.now().strftime('%Y%m%d_%H')}"
                if uid in self._seen_ids:
                    continue

                # Read the actual message content
                message_text = self._read_last_message(el)

                # Only create action if message contains a trigger keyword
                if not message_text or not self._contains_trigger_keyword(message_text):
                    continue

                self._seen_ids.add(uid)
                unread.append({
                    'type': 'whatsapp_message',
                    'contact': contact,
                    'message_text': message_text,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'unread',
                })
        except Exception as e:
            logger.error(f"Error checking WhatsApp: {e}")

        return unread

    def _generate_draft_reply(self, contact: str, message_text: str) -> str:
        """Generate a simple draft reply based on the message content"""
        text_lower = message_text.lower()
        if 'urgent' in text_lower:
            return f"Hi {contact}, I received your urgent message and will get back to you shortly. Thank you for reaching out."
        return f"Hi {contact}, thank you for your message. I'll review and respond soon."

    def create_action_file(self, item) -> Path:
        """Create an action file for a WhatsApp message with content and draft reply"""
        ts = int(datetime.now().timestamp())
        safe_contact = "".join(c if c.isalnum() or c in '-_' else '_' for c in item['contact'])
        filename = f"whatsapp_{safe_contact}_{ts}.md"
        filepath = self.needs_action / filename

        message_text = item.get('message_text', '')
        draft_reply = self._generate_draft_reply(item['contact'], message_text)

        content = f"""---
action_type: whatsapp_message
contact: {item['contact']}
---
# WhatsApp Message Alert: {item['contact']}

## Message Details
- **Source**: WhatsApp
- **Contact**: {item['contact']}
- **Received**: {item['timestamp']}
- **Status**: {item['status']}

## Message Content
> {message_text}

## Draft Reply
{draft_reply}

## Action Required
Review the message from {item['contact']} and approve or edit the draft reply above.
"""
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created WhatsApp action file: {filepath.name}")
        return filepath

    def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


if __name__ == "__main__":
    from utils.logger import setup_logger
    from utils.config_loader import load_config

    config = load_config()
    setup_logger(config.get('LOG_LEVEL', 'INFO'))
    watcher = WhatsAppWatcher(config['VAULT_PATH'])
    try:
        watcher.run()
    except KeyboardInterrupt:
        watcher.cleanup()
