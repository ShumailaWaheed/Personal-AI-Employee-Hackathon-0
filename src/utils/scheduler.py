"""
Scheduler
Manages scheduled task execution using file-based state persistence.
Checks if tasks are due based on day-of-week + time schedules.
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

DAY_MAP = {
    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
    'friday': 4, 'saturday': 5, 'sunday': 6,
}


class Scheduler:
    """Manages scheduled tasks with file-based state persistence"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.state_path = self.vault_path / 'Business' / 'scheduler_state.json'
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._schedules: dict[str, str] = {}
        self._state: dict = {}
        self._state = self._load_state()

    def configure(self, task_name: str, schedule: str):
        """Register a task with its schedule (e.g., 'monday:09:00')"""
        self._schedules[task_name] = schedule

    def is_due(self, task_name: str) -> bool:
        """Check if a scheduled task is due for execution"""
        schedule = self._schedules.get(task_name)
        if not schedule:
            return False

        now = datetime.now()
        target_day, target_hour, target_minute = self._parse_schedule(schedule)
        target_day_num = DAY_MAP.get(target_day, 0)

        # Check if we've already run this period
        task_state = self._state.get(task_name, {})
        last_run_str = task_state.get('last_run')

        if last_run_str:
            try:
                last_run = datetime.fromisoformat(last_run_str)
                # Calculate next scheduled run after last_run
                next_run = self._next_occurrence(last_run, target_day_num, target_hour, target_minute)
                if now < next_run:
                    return False
            except (ValueError, TypeError):
                pass

        # Check if today is the right day and we're past the target time
        if now.weekday() == target_day_num:
            target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            return now >= target_time

        # If never run, it's due
        if not last_run_str:
            return True

        return False

    def mark_completed(self, task_name: str):
        """Mark a scheduled task as completed"""
        now = datetime.now()
        schedule = self._schedules.get(task_name, '')

        self._state[task_name] = {
            'schedule': schedule,
            'last_run': now.isoformat(),
            'status': 'completed',
        }

        # Calculate next run
        if schedule:
            target_day, target_hour, target_minute = self._parse_schedule(schedule)
            target_day_num = DAY_MAP.get(target_day, 0)
            next_run = self._next_occurrence(now, target_day_num, target_hour, target_minute)
            self._state[task_name]['next_run'] = next_run.isoformat()

        self._save_state()
        logger.info(f"Scheduled task completed: {task_name}")

    def _parse_schedule(self, schedule: str) -> tuple[str, int, int]:
        """Parse a schedule string like 'monday:09:00' into components"""
        try:
            parts = schedule.lower().split(':')
            if len(parts) >= 3:
                day = parts[0].strip()
                hour = int(parts[1].strip())
                minute = int(parts[2].strip())
                if day in DAY_MAP:
                    return day, hour, minute
        except (ValueError, IndexError):
            pass
        return 'monday', 9, 0

    def _next_occurrence(self, after: datetime, target_day: int,
                          target_hour: int, target_minute: int) -> datetime:
        """Calculate the next occurrence of a weekly schedule after a given datetime"""
        days_ahead = target_day - after.weekday()
        if days_ahead <= 0:
            days_ahead += 7

        next_date = after + timedelta(days=days_ahead)
        return next_date.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

    def _load_state(self) -> dict:
        """Load scheduler state from JSON file"""
        if not self.state_path.exists():
            return {}
        try:
            return json.loads(self.state_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load scheduler state: {e}")
            return {}

    def _save_state(self):
        """Save scheduler state to JSON file"""
        self.state_path.write_text(json.dumps(self._state, indent=2), encoding='utf-8')
