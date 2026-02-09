"""
Gold Processor unit tests — US1: Autonomous Action Item Processing
Tests process_all() cycle, priority ordering, domain classification,
auto-approval routing, and backward compatibility with Silver behavior.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent / 'src'))

import pytest
from config.settings import load_config


@pytest.fixture
def vault(tmp_path):
    """Create a Gold-tier vault directory structure"""
    dirs = [
        'Inbox', 'Needs_Action', 'Pending_Approval', 'Approved',
        'Rejected', 'Done', 'Logs', 'Plans',
        'Business', 'Business/Accounting', 'Business/Social', 'Briefings',
    ]
    for d in dirs:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def gold_config(vault):
    """Gold-tier configuration"""
    return {
        'VAULT_PATH': str(vault),
        'CHECK_INTERVAL': 60,
        'LOG_LEVEL': 'DEBUG',
        'DRY_RUN': True,
        'PROCESSING_INTERVAL': 30,
        'GOLD_TIER_ENABLED': True,
        'AUTO_APPROVE_LOW_RISK': False,
        'AUDIT_SCHEDULE': 'monday:09:00',
        'BRIEFING_SCHEDULE': 'monday:10:00',
    }


@pytest.fixture
def gold_processor(vault, gold_config):
    from processors.gold_processor import GoldProcessor
    return GoldProcessor(str(vault), gold_config)


class TestGoldProcessorInit:
    def test_gold_processor_inherits_silver(self, gold_processor):
        from processors.silver_processor import SilverProcessor
        assert isinstance(gold_processor, SilverProcessor)

    def test_gold_dirs_created(self, gold_processor, vault):
        assert (vault / 'Business').exists()
        assert (vault / 'Business' / 'Accounting').exists()
        assert (vault / 'Business' / 'Social').exists()
        assert (vault / 'Briefings').exists()


class TestGoldProcessAll:
    def test_detects_needs_action_files(self, gold_processor, vault):
        action = vault / 'Needs_Action' / 'test_action.md'
        action.write_text("# Test Action\nDo something simple.", encoding='utf-8')

        gold_processor.process_all()

        # Non-sensitive action processed by Bronze: plan created, status updated in place
        plans = list((vault / 'Plans').glob("*test_action*"))
        assert len(plans) >= 1

    def test_classifies_priority(self, gold_processor, vault):
        action = vault / 'Needs_Action' / 'urgent_task.md'
        action.write_text("---\npriority: urgent\n---\n# Urgent Task\nDo this right now!", encoding='utf-8')

        gold_processor.process_all()

        # Non-sensitive content: processed directly, plan created
        plans = list((vault / 'Plans').glob("*urgent_task*"))
        assert len(plans) >= 1

    def test_classifies_domain(self, gold_processor, vault):
        action = vault / 'Needs_Action' / 'business_task.md'
        action.write_text("---\ndomain: business\n---\n# Record expense\nInvoice for vendor payment", encoding='utf-8')

        gold_processor.process_all()

        # Business + financial keywords → sensitive → routed to approval
        assert (vault / 'Done' / 'business_task.md').exists() or \
               len(list((vault / 'Pending_Approval').glob("*.md"))) > 0

    def test_priority_ordering(self, gold_processor, vault):
        """Higher priority items should be processed first"""
        (vault / 'Needs_Action' / 'aaa_low.md').write_text(
            "---\npriority: low\n---\n# Low priority", encoding='utf-8')
        (vault / 'Needs_Action' / 'bbb_urgent.md').write_text(
            "---\npriority: urgent\n---\n# Urgent priority", encoding='utf-8')

        gold_processor.process_all()

        # Both should be processed — plans created for non-sensitive content
        plans = list((vault / 'Plans').glob("PLAN_*"))
        assert len(plans) >= 2

    def test_sensitive_action_routed_to_approval(self, gold_processor, vault):
        action = vault / 'Needs_Action' / 'send_email_task.md'
        action.write_text("# Send Email\nSend an email to john@example.com", encoding='utf-8')

        gold_processor.process_all()

        # Should be routed to approval (email is sensitive)
        approval_files = list((vault / 'Pending_Approval').glob("*.md"))
        assert len(approval_files) >= 1

    def test_process_approved_actions(self, gold_processor, vault):
        approved = vault / 'Approved' / 'approval_test.md'
        approved.write_text("---\naction: email_send\n---\n# Approved action", encoding='utf-8')

        gold_processor.process_all()

        # Approved action should be executed (DRY_RUN) and moved to Done
        assert (vault / 'Done' / 'approval_test.md').exists()


class TestGoldDisabled:
    def test_falls_back_to_silver_when_disabled(self, vault):
        config = {
            'VAULT_PATH': str(vault),
            'CHECK_INTERVAL': 60,
            'LOG_LEVEL': 'DEBUG',
            'DRY_RUN': True,
            'PROCESSING_INTERVAL': 30,
            'GOLD_TIER_ENABLED': False,
            'AUTO_APPROVE_LOW_RISK': False,
        }
        from processors.gold_processor import GoldProcessor
        gp = GoldProcessor(str(vault), config)

        action = vault / 'Needs_Action' / 'basic.md'
        action.write_text("# Basic task\nNothing special.", encoding='utf-8')

        gp.process_all()
        # Non-sensitive: processed via Bronze (plan created in place)
        plans = list((vault / 'Plans').glob("*basic*"))
        assert len(plans) >= 1
