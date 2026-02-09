"""
Performance Tracker
Monitors posted content performance metrics
"""
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Tracks performance of posted LinkedIn content"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.tracking_file = self.vault_path / 'Logs' / 'post_performance.json'

    def record_post(self, post_id: str, content_preview: str, platform: str = "linkedin"):
        """Record a new post for tracking"""
        records = self._load()
        records.append({
            "post_id": post_id,
            "platform": platform,
            "content_preview": content_preview[:100],
            "posted_at": datetime.now().isoformat(),
            "status": "posted",
        })
        self._save(records)

    def get_posts(self, limit: int = 10) -> list[dict]:
        """Get recent tracked posts"""
        records = self._load()
        return records[-limit:]

    def _load(self) -> list:
        if self.tracking_file.exists():
            try:
                return json.loads(self.tracking_file.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                pass
        return []

    def _save(self, records: list):
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        self.tracking_file.write_text(json.dumps(records, indent=2), encoding='utf-8')
