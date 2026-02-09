"""
Scheduler tests — US4: Weekly Business Audit & Executive Briefing
Tests schedule checking, state persistence, schedule parsing, next_run calculation.
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent / 'src'))

import pytest


@pytest.fixture
def vault(tmp_path):
    (tmp_path / 'Business').mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestScheduler:
    def test_is_due_when_never_run(self, vault):
        from utils.scheduler import Scheduler
        sched = Scheduler(str(vault))
        # First run should always be due (never run before)
        # We need to set the schedule to a day/time that has passed
        sched._schedules['test_task'] = 'monday:00:00'
        assert sched.is_due('test_task') is True

    def test_is_due_returns_false_when_recently_run(self, vault):
        from utils.scheduler import Scheduler
        sched = Scheduler(str(vault))
        sched._schedules['test_task'] = 'monday:00:00'
        sched.mark_completed('test_task')
        # Just marked complete — should not be due again
        assert sched.is_due('test_task') is False

    def test_state_persistence(self, vault):
        from utils.scheduler import Scheduler
        sched1 = Scheduler(str(vault))
        sched1._schedules['persist_test'] = 'monday:09:00'
        sched1.mark_completed('persist_test')

        # Load fresh instance
        sched2 = Scheduler(str(vault))
        state = sched2._load_state()
        assert 'persist_test' in state

    def test_schedule_parsing(self, vault):
        from utils.scheduler import Scheduler
        sched = Scheduler(str(vault))
        day, hour, minute = sched._parse_schedule('wednesday:14:30')
        assert day == 'wednesday'
        assert hour == 14
        assert minute == 30

    def test_invalid_schedule_returns_defaults(self, vault):
        from utils.scheduler import Scheduler
        sched = Scheduler(str(vault))
        day, hour, minute = sched._parse_schedule('invalid')
        assert day == 'monday'
        assert hour == 9
        assert minute == 0

    def test_mark_completed_updates_state(self, vault):
        from utils.scheduler import Scheduler
        sched = Scheduler(str(vault))
        sched._schedules['complete_test'] = 'friday:08:00'
        sched.mark_completed('complete_test')

        state = sched._load_state()
        assert 'complete_test' in state
        assert 'last_run' in state['complete_test']
        assert state['complete_test']['status'] == 'completed'
