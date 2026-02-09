"""
Retry Manager
Manages a persistent retry queue stored as Markdown in the vault
"""
import logging
from pathlib import Path
from datetime import datetime

from models.retry_queue_entry import RetryQueueEntry

logger = logging.getLogger(__name__)


class RetryManager:
    """Manages retry queue for failed MCP operations"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.queue_path = self.vault_path / 'Business' / 'retry_queue.md'
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[RetryQueueEntry] = []
        self.load_queue()

    def load_queue(self):
        """Load retry queue from Markdown file"""
        self._entries = []
        if not self.queue_path.exists():
            return

        content = self.queue_path.read_text(encoding='utf-8')
        sections = content.split('## Retry:')

        for section in sections[1:]:  # Skip header
            section = '## Retry:' + section
            try:
                entry = RetryQueueEntry.from_markdown(section)
                if entry.id:
                    self._entries.append(entry)
            except Exception as e:
                logger.warning(f"Failed to parse retry entry: {e}")

    def save_queue(self):
        """Save retry queue to Markdown file"""
        if not self._entries:
            self.queue_path.write_text(
                "# Retry Queue\n\nNo pending retries.\n",
                encoding='utf-8',
            )
            return

        lines = ["# Retry Queue\n"]
        for entry in self._entries:
            lines.append(entry.to_markdown())

        self.queue_path.write_text("\n".join(lines), encoding='utf-8')

    def add_to_queue(self, entry: RetryQueueEntry):
        """Add a new entry to the retry queue"""
        entry.calculate_next_retry()
        self._entries.append(entry)
        self.save_queue()
        logger.info(f"Added to retry queue: {entry.id} (attempt {entry.retry_count}/{entry.max_retries})")

    def get_ready_entries(self) -> list[RetryQueueEntry]:
        """Get entries that are due for retry"""
        now = datetime.now()
        ready = []
        for entry in self._entries:
            if entry.status == 'queued' and entry.next_retry_after and entry.next_retry_after <= now:
                ready.append(entry)
        return ready

    def update_entry(self, entry_id: str, status: str, error: str = ""):
        """Update an entry's status"""
        for entry in self._entries:
            if entry.id == entry_id:
                entry.status = status
                if error:
                    entry.error = error
                if status == 'queued':
                    entry.retry_count += 1
                    entry.last_attempt = datetime.now()
                    if entry.retry_count >= entry.max_retries:
                        entry.status = 'failed_permanent'
                    else:
                        entry.calculate_next_retry()
                self.save_queue()
                return
        logger.warning(f"Retry entry not found: {entry_id}")

    def remove_entry(self, entry_id: str):
        """Remove an entry from the queue (on success)"""
        self._entries = [e for e in self._entries if e.id != entry_id]
        self.save_queue()
        logger.info(f"Removed from retry queue: {entry_id}")

    @property
    def queue_depth(self) -> int:
        return len(self._entries)

    @property
    def entries(self) -> list[RetryQueueEntry]:
        return list(self._entries)
