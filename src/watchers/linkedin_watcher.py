"""
LinkedIn Watcher Implementation
Monitors LinkedIn for updates using the Marketing Developer API with OAuth2
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from watchers.base_watcher import BaseWatcher

logger = logging.getLogger(__name__)


class LinkedInWatcher(BaseWatcher):
    def __init__(self, vault_path: str, check_interval: int = 300):
        super().__init__(vault_path, check_interval)
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
        self.account_id = os.getenv('LINKEDIN_PERSONAL_ACCOUNT_ID', '')
        self.api_base = "https://api.linkedin.com/v2"
        self._last_connection_count: int | None = None

    def _headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json',
        }

    def check_for_updates(self) -> list:
        """Check LinkedIn for new activity"""
        if not self.access_token:
            logger.warning("LINKEDIN_ACCESS_TOKEN not set, skipping LinkedIn check")
            return []

        updates = []
        try:
            import requests
        except ImportError:
            logger.error("requests not installed. Run: pip install requests")
            return []

        # Check connection count changes
        try:
            url = f"{self.api_base}/connections?q=viewer&start=0&count=0"
            resp = requests.get(url, headers=self._headers(), timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                total = data.get('paging', {}).get('total', 0)
                if self._last_connection_count is not None and total != self._last_connection_count:
                    updates.append({
                        'type': 'linkedin_update',
                        'update_type': 'connection_count_change',
                        'detail': f"Connections: {self._last_connection_count} -> {total}",
                        'timestamp': datetime.now().isoformat(),
                    })
                self._last_connection_count = total
            elif resp.status_code == 401:
                logger.error("LinkedIn API: unauthorized - token may be expired")
            else:
                logger.warning(f"LinkedIn API returned {resp.status_code}")
        except Exception as e:
            logger.error(f"Error checking LinkedIn connections: {e}")

        # Check for notifications / mentions (simplified)
        try:
            url = f"{self.api_base}/socialActions?q=actor&actor=urn:li:person:{self.account_id}&count=5"
            resp = requests.get(url, headers=self._headers(), timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                elements = data.get('elements', [])
                if elements:
                    updates.append({
                        'type': 'linkedin_update',
                        'update_type': 'social_activity',
                        'detail': f"{len(elements)} recent social actions",
                        'timestamp': datetime.now().isoformat(),
                    })
        except Exception as e:
            logger.error(f"Error checking LinkedIn activity: {e}")

        return updates

    def create_action_file(self, item) -> Path:
        """Create an action file for LinkedIn updates"""
        ts = int(datetime.now().timestamp())
        filename = f"linkedin_{item['update_type']}_{ts}.md"
        filepath = self.needs_action / filename

        content = f"""# LinkedIn Update Notification

## Update Details
- **Source**: LinkedIn
- **Type**: {item['update_type']}
- **Detail**: {item.get('detail', 'N/A')}
- **Occurred**: {item['timestamp']}

## Action Required
Review LinkedIn account for new activity and determine appropriate response.

## Recommended Actions
- Engage with new connections
- Respond to comments on recent posts
- Create new content based on network activity
"""
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created LinkedIn action file: {filepath.name}")
        return filepath


if __name__ == "__main__":
    from utils.logger import setup_logger
    from utils.config_loader import load_config

    config = load_config()
    setup_logger(config.get('LOG_LEVEL', 'INFO'))
    watcher = LinkedInWatcher(config['VAULT_PATH'])
    watcher.run()
