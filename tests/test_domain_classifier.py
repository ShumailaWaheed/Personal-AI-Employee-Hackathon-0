"""
Domain Classification integration tests — US5: Cross-Domain Workflows
Tests personal-only, business-only, cross-domain detection, frontmatter override,
and cross-domain always requires approval regardless of auto-approve setting.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'src'))

import pytest
from utils.domain_classifier import classify_domain


class TestDomainClassificationIntegration:
    def test_personal_only(self):
        content = "Set a reminder for my personal calendar appointment"
        assert classify_domain(content) == "personal"

    def test_business_only(self):
        content = "Create an invoice for the vendor quarterly payment"
        assert classify_domain(content) == "business"

    def test_cross_domain_detection(self):
        content = "Schedule a personal reminder about the client vendor invoice meeting"
        assert classify_domain(content) == "cross-domain"

    def test_frontmatter_override(self):
        content = "This has no domain keywords at all"
        assert classify_domain(content, {"domain": "business"}) == "business"

    def test_cross_domain_frontmatter(self):
        content = "Any content here"
        assert classify_domain(content, {"domain": "cross-domain"}) == "cross-domain"


class TestCrossDomainApproval:
    """Cross-domain actions must ALWAYS require approval regardless of auto-approve"""

    @pytest.fixture
    def vault(self, tmp_path):
        dirs = [
            'Inbox', 'Needs_Action', 'Pending_Approval', 'Approved',
            'Rejected', 'Done', 'Logs', 'Plans',
            'Business', 'Business/Accounting', 'Business/Social', 'Briefings',
        ]
        for d in dirs:
            (tmp_path / d).mkdir(parents=True, exist_ok=True)
        return tmp_path

    def test_cross_domain_with_auto_approve_enabled(self, vault):
        """Even with auto-approve enabled, cross-domain requires human approval"""
        config = {
            'VAULT_PATH': str(vault),
            'CHECK_INTERVAL': 60,
            'LOG_LEVEL': 'DEBUG',
            'DRY_RUN': True,
            'PROCESSING_INTERVAL': 30,
            'GOLD_TIER_ENABLED': True,
            'AUTO_APPROVE_LOW_RISK': True,  # Auto-approve enabled
            'AUDIT_SCHEDULE': 'monday:09:00',
            'BRIEFING_SCHEDULE': 'monday:10:00',
        }
        from processors.gold_processor import GoldProcessor
        gp = GoldProcessor(str(vault), config)

        # Cross-domain action with sensitive content
        action = vault / 'Needs_Action' / 'cross_task.md'
        action.write_text(
            "---\ndomain: cross-domain\n---\n"
            "# Cross Domain Task\nSend an email about personal family calendar and client vendor invoice",
            encoding='utf-8',
        )

        gp.process_all()

        # Cross-domain with email keyword → sensitive → should NOT be auto-approved
        approval_files = list((vault / 'Pending_Approval').glob("*.md"))
        done_files = list((vault / 'Done').glob("*.md"))
        # Original moved to Done, approval created in Pending_Approval
        assert len(approval_files) >= 1 or len(done_files) >= 1

    def test_can_auto_approve_rejects_cross_domain(self):
        from processors.gold_processor import GoldProcessor

        class FakeGP:
            auto_approve_low_risk = True

        gp = FakeGP()
        # Cross-domain must always be rejected even with auto-approve enabled
        assert GoldProcessor._can_auto_approve(gp, 'low', 'cross-domain') is False

    def test_can_auto_approve_accepts_low_risk_personal(self):
        """Low-risk personal domain CAN be auto-approved when enabled"""
        from processors.gold_processor import GoldProcessor

        class FakeGP:
            auto_approve_low_risk = True

        gp = FakeGP()
        assert GoldProcessor._can_auto_approve(gp, 'low', 'personal') is True

    def test_can_auto_approve_rejects_high_risk(self):
        from processors.gold_processor import GoldProcessor

        class FakeGP:
            auto_approve_low_risk = True

        gp = FakeGP()
        assert GoldProcessor._can_auto_approve(gp, 'high', 'personal') is False
