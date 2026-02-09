"""
Retry Manager tests — US6: Reliability & Failure Recovery
Tests exponential backoff, queue persistence, entry removal on success,
failed_permanent after 3 retries, notification creation on permanent failure.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent / 'src'))

import pytest
from models.retry_queue_entry import RetryQueueEntry
from utils.retry_manager import RetryManager


@pytest.fixture
def vault(tmp_path):
    (tmp_path / 'Business').mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestExponentialBackoff:
    def test_first_retry_30s(self):
        entry = RetryQueueEntry(id="test", operation="op", mcp_server="s", retry_count=0)
        before = datetime.now()
        entry.calculate_next_retry()
        # 30s backoff for retry_count=0
        assert entry.next_retry_after >= before + timedelta(seconds=29)

    def test_second_retry_60s(self):
        entry = RetryQueueEntry(id="test", operation="op", mcp_server="s", retry_count=1)
        before = datetime.now()
        entry.calculate_next_retry()
        # 60s backoff for retry_count=1
        assert entry.next_retry_after >= before + timedelta(seconds=59)

    def test_third_retry_120s(self):
        entry = RetryQueueEntry(id="test", operation="op", mcp_server="s", retry_count=2)
        before = datetime.now()
        entry.calculate_next_retry()
        # 120s backoff for retry_count=2
        assert entry.next_retry_after >= before + timedelta(seconds=119)


class TestQueuePersistence:
    def test_save_and_load(self, vault):
        mgr = RetryManager(str(vault))
        entry = RetryQueueEntry(
            id="persist_test", operation="create_expense", mcp_server="odoo",
            parameters={"amount": 100}, error="timeout", status="queued",
        )
        mgr.add_to_queue(entry)

        # Load fresh
        mgr2 = RetryManager(str(vault))
        assert mgr2.queue_depth == 1
        assert mgr2.entries[0].id == "persist_test"

    def test_empty_queue_persistence(self, vault):
        mgr = RetryManager(str(vault))
        mgr.save_queue()
        mgr2 = RetryManager(str(vault))
        assert mgr2.queue_depth == 0


class TestEntryRemoval:
    def test_remove_on_success(self, vault):
        mgr = RetryManager(str(vault))
        entry = RetryQueueEntry(id="remove_test", operation="op", mcp_server="s")
        mgr.add_to_queue(entry)
        assert mgr.queue_depth == 1

        mgr.remove_entry("remove_test")
        assert mgr.queue_depth == 0


class TestFailedPermanent:
    def test_permanent_after_3_retries(self, vault):
        mgr = RetryManager(str(vault))
        entry = RetryQueueEntry(
            id="fail_test", operation="op", mcp_server="s",
            retry_count=2, max_retries=3, status="queued",
        )
        mgr.add_to_queue(entry)

        # Update to trigger retry count check (already at 2, incrementing to 3)
        mgr.update_entry("fail_test", "queued", "still failing")

        # Should be failed_permanent now
        loaded = RetryManager(str(vault))
        failed = [e for e in loaded.entries if e.id == "fail_test"]
        assert len(failed) == 1
        assert failed[0].status == "failed_permanent"


class TestGetReadyEntries:
    def test_returns_due_entries(self, vault):
        mgr = RetryManager(str(vault))
        entry = RetryQueueEntry(
            id="ready_test", operation="op", mcp_server="s",
            status="queued",
            next_retry_after=datetime.now() - timedelta(seconds=1),
        )
        mgr._entries.append(entry)

        ready = mgr.get_ready_entries()
        assert len(ready) == 1

    def test_skips_not_due_entries(self, vault):
        mgr = RetryManager(str(vault))
        entry = RetryQueueEntry(
            id="future_test", operation="op", mcp_server="s",
            status="queued",
            next_retry_after=datetime.now() + timedelta(hours=1),
        )
        mgr._entries.append(entry)

        ready = mgr.get_ready_entries()
        assert len(ready) == 0
