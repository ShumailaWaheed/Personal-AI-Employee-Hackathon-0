"""
Rate Limiter for Social Media Posts
Enforces 1-3 posts per day limit for LinkedIn
"""
import json
import logging
from pathlib import Path
from datetime import datetime, date

logger = logging.getLogger(__name__)


class RateLimiter:
    """Enforces daily posting limits for LinkedIn"""

    def __init__(self, vault_path: str, max_posts_per_day: int = 3):
        self.vault_path = Path(vault_path)
        self.max_posts = max_posts_per_day
        self.state_file = self.vault_path / 'Logs' / '.rate_limiter_state.json'

    def _load_state(self) -> dict:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                pass
        return {"date": str(date.today()), "count": 0}

    def _save_state(self, state: dict):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(state), encoding='utf-8')

    def can_post(self) -> bool:
        """Check if posting is allowed under rate limits"""
        state = self._load_state()
        today = str(date.today())

        if state["date"] != today:
            # New day, reset counter
            return True

        return state["count"] < self.max_posts

    def record_post(self):
        """Record that a post was made"""
        state = self._load_state()
        today = str(date.today())

        if state["date"] != today:
            state = {"date": today, "count": 0}

        state["count"] += 1
        self._save_state(state)
        logger.info(f"LinkedIn posts today: {state['count']}/{self.max_posts}")

    def remaining_posts(self) -> int:
        """Get the number of posts remaining today"""
        state = self._load_state()
        today = str(date.today())

        if state["date"] != today:
            return self.max_posts

        return max(0, self.max_posts - state["count"])
