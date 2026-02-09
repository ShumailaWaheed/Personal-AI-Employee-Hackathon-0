"""
Log Manager
Implements log rotation and retention policies for audit logs
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LogManager:
    """Manages log rotation and retention for audit logs"""

    def __init__(self, vault_path: str, retention_days: int = 90):
        self.logs_dir = Path(vault_path) / 'Logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days

    def rotate(self):
        """Remove log files older than retention period"""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        removed = 0
        for log_file in self.logs_dir.glob("*.json"):
            try:
                date_str = log_file.stem  # e.g., 2026-02-06
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                if file_date < cutoff:
                    log_file.unlink()
                    removed += 1
                    logger.info(f"Rotated old log: {log_file.name}")
            except (ValueError, OSError):
                continue
        if removed:
            logger.info(f"Rotated {removed} old log file(s)")

    def get_log_summary(self, days: int = 7) -> dict:
        """Get summary statistics for recent logs"""
        summary = {
            "total_entries": 0,
            "success_count": 0,
            "failure_count": 0,
            "action_types": {},
            "days_covered": 0,
        }
        cutoff = datetime.now() - timedelta(days=days)

        for log_file in sorted(self.logs_dir.glob("*.json")):
            try:
                date_str = log_file.stem
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                if file_date < cutoff:
                    continue
                entries = json.loads(log_file.read_text(encoding='utf-8'))
                summary["days_covered"] += 1
                for entry in entries:
                    summary["total_entries"] += 1
                    result = entry.get("result", "unknown")
                    if result == "success":
                        summary["success_count"] += 1
                    else:
                        summary["failure_count"] += 1
                    atype = entry.get("action_type", "unknown")
                    summary["action_types"][atype] = summary["action_types"].get(atype, 0) + 1
            except (ValueError, json.JSONDecodeError, OSError):
                continue

        return summary
