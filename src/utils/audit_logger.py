"""
Audit Logger
Creates structured JSON audit log entries following constitution format.
Logs are stored in /Logs/YYYY-MM-DD.json with PII sanitization.
"""
import json
import logging
from pathlib import Path
from datetime import datetime

from models.audit_log_entry import AuditLogEntry
from utils.log_sanitizer import sanitize_entry

logger = logging.getLogger(__name__)


class AuditLogger:
    """Structured JSON audit logger for the AI Employee system"""

    def __init__(self, vault_path: str):
        self.logs_dir = Path(vault_path) / 'Logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def log(self, entry: AuditLogEntry):
        """Write a sanitized audit log entry to today's log file"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = self.logs_dir / f"{today}.json"

        sanitized = sanitize_entry(entry.to_dict())

        entries = []
        if log_path.exists():
            try:
                entries = json.loads(log_path.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                entries = []

        entries.append(sanitized)
        log_path.write_text(json.dumps(entries, indent=2), encoding='utf-8')
        logger.debug(f"Logged: {entry.action_type} -> {entry.result}")

    def get_recent(self, count: int = 10) -> list[dict]:
        """Get the most recent audit log entries"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = self.logs_dir / f"{today}.json"
        if not log_path.exists():
            return []
        try:
            entries = json.loads(log_path.read_text(encoding='utf-8'))
            return entries[-count:]
        except (json.JSONDecodeError, OSError):
            return []
