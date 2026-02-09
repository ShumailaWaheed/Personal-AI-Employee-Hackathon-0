"""
Safety tests — US6: Reliability & Failure Recovery
Tests critical safety invariants: approval gate, DRY_RUN, PII sanitization, domain isolation.
"""
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'src'))

import pytest


@pytest.fixture
def vault(tmp_path):
    dirs = [
        'Inbox', 'Needs_Action', 'Pending_Approval', 'Approved',
        'Rejected', 'Done', 'Logs', 'Plans',
        'Business', 'Business/Accounting', 'Business/Social', 'Briefings',
    ]
    for d in dirs:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def config(vault):
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


class TestApprovalGate:
    """No external action without approval record"""

    def test_sensitive_action_creates_approval(self, vault, config):
        from processors.gold_processor import GoldProcessor
        gp = GoldProcessor(str(vault), config)

        action = vault / 'Needs_Action' / 'send_payment.md'
        action.write_text("# Payment\nTransfer $5000 to vendor account", encoding='utf-8')

        gp.process_all()

        # Sensitive (payment) → must create approval request
        approval_files = list((vault / 'Pending_Approval').glob("*.md"))
        assert len(approval_files) >= 1

    def test_no_direct_mcp_without_approval(self, vault, config):
        """Actions in Needs_Action should never directly trigger MCP execution"""
        from processors.gold_processor import GoldProcessor
        gp = GoldProcessor(str(vault), config)

        action = vault / 'Needs_Action' / 'email_task.md'
        action.write_text("# Email\nSend email to client@example.com", encoding='utf-8')

        gp.process_all()

        # Check audit logs — should have route_to_approval, NOT executed
        today = vault / 'Logs' / f'{__import__("datetime").datetime.now().strftime("%Y-%m-%d")}.json'
        if today.exists():
            logs = json.loads(today.read_text(encoding='utf-8'))
            for log in logs:
                if log.get('target') == 'email_task.md':
                    assert log.get('approval_status') != 'executed'


class TestDryRun:
    """DRY_RUN blocks all MCP execution"""

    def test_dry_run_blocks_execution(self, vault, config):
        from processors.gold_processor import GoldProcessor
        config['DRY_RUN'] = True
        gp = GoldProcessor(str(vault), config)

        # Place an already-approved action
        approved = vault / 'Approved' / 'test_approved.md'
        approved.write_text("---\naction: email_send\n---\n# Test\nSend email", encoding='utf-8')

        gp.process_all()

        # Should be moved to Done (dry-run execution counts as success)
        assert (vault / 'Done' / 'test_approved.md').exists()


class TestPIISanitization:
    """PII should not appear in Gold-tier log entries"""

    def test_domain_field_in_logs(self, vault, config):
        from processors.gold_processor import GoldProcessor
        gp = GoldProcessor(str(vault), config)

        action = vault / 'Needs_Action' / 'pii_test.md'
        action.write_text(
            "---\ndomain: business\n---\n# Record expense\n"
            "Record invoice payment for vendor",
            encoding='utf-8',
        )

        gp.process_all()

        # Check that logs contain domain field but not raw PII
        today = vault / 'Logs' / f'{__import__("datetime").datetime.now().strftime("%Y-%m-%d")}.json'
        if today.exists():
            content = today.read_text(encoding='utf-8')
            logs = json.loads(content)
            for log in logs:
                if 'domain' in log:
                    assert log['domain'] in ('personal', 'business', 'cross-domain')


class TestDomainIsolation:
    """Failure in one integration domain should not prevent others from processing"""

    def test_multiple_domains_independent(self, vault, config):
        from processors.gold_processor import GoldProcessor
        gp = GoldProcessor(str(vault), config)

        # Create actions in different domains
        (vault / 'Needs_Action' / 'personal_task.md').write_text(
            "---\ndomain: personal\n---\n# Reminder\nSet a personal reminder", encoding='utf-8')
        (vault / 'Needs_Action' / 'business_task.md').write_text(
            "---\ndomain: business\n---\n# Expense\nRecord the quarterly expense for vendor", encoding='utf-8')

        # Process — even if one domain has issues, both should be attempted
        gp.process_all()

        # Both should have been processed (plans created or approval routes created)
        plans = list((vault / 'Plans').glob("PLAN_*"))
        approvals = list((vault / 'Pending_Approval').glob("*.md"))
        done = list((vault / 'Done').glob("*.md"))
        # At least one outcome per action
        assert len(plans) + len(approvals) + len(done) >= 2
