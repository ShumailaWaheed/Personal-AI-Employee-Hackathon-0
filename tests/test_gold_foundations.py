"""
Foundational tests for Gold tier models, classifiers, and utilities.
Tests backward compatibility of extended models and correctness of new components.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent / 'src'))

import pytest
from models.action_file import ActionFile
from models.approval_request import ApprovalRequest
from models.audit_log_entry import AuditLogEntry
from models.retry_queue_entry import RetryQueueEntry
from models.mcp_server_status import MCPServerStatus
from models.audit_report import AuditReportModel
from utils.priority_classifier import classify_priority, parse_frontmatter
from utils.domain_classifier import classify_domain


# ── ActionFile backward compatibility ────────────────────────────────────

class TestActionFileExtended:
    def test_default_priority_is_normal(self):
        af = ActionFile("test.md", Path("/tmp/test.md"), "general", "content")
        assert af.priority == "normal"

    def test_domain_defaults_none(self):
        af = ActionFile("test.md", Path("/tmp/test.md"), "general", "content")
        assert af.domain is None

    def test_processor_defaults_none(self):
        af = ActionFile("test.md", Path("/tmp/test.md"), "general", "content")
        assert af.processor is None

    def test_to_dict_without_gold_fields(self):
        af = ActionFile("test.md", Path("/tmp/test.md"), "general", "content")
        d = af.to_dict()
        assert "domain" not in d
        assert "processor" not in d

    def test_to_dict_with_gold_fields(self):
        af = ActionFile("test.md", Path("/tmp/test.md"), "general", "content",
                        domain="business", processor="gold_processor")
        d = af.to_dict()
        assert d["domain"] == "business"
        assert d["processor"] == "gold_processor"

    def test_backward_compatible_creation(self):
        af = ActionFile("test.md", Path("/tmp/test.md"), "general", "content", priority="normal", status="pending")
        assert af.id == "test"
        assert af.status == "pending"


# ── ApprovalRequest backward compatibility ────────────────────────────────

class TestApprovalRequestExtended:
    def test_approval_source_defaults_none(self):
        ar = ApprovalRequest("email_send", "user@example.com")
        assert ar.approval_source is None

    def test_domain_defaults_none(self):
        ar = ApprovalRequest("email_send", "user@example.com")
        assert ar.domain is None

    def test_to_frontmatter_without_gold_fields(self):
        ar = ApprovalRequest("email_send", "user@example.com")
        fm = ar.to_frontmatter()
        assert "domain:" not in fm
        assert "approval_source:" not in fm

    def test_to_frontmatter_with_gold_fields(self):
        ar = ApprovalRequest("email_send", "user@example.com",
                             domain="business", approval_source="auto")
        fm = ar.to_frontmatter()
        assert "domain: business" in fm
        assert "approval_source: auto" in fm

    def test_to_dict_without_gold_fields(self):
        ar = ApprovalRequest("email_send", "user@example.com")
        d = ar.to_dict()
        assert "approval_source" not in d
        assert "domain" not in d

    def test_to_dict_with_gold_fields(self):
        ar = ApprovalRequest("email_send", "user@example.com",
                             approval_source="human", domain="personal")
        d = ar.to_dict()
        assert d["approval_source"] == "human"
        assert d["domain"] == "personal"


# ── AuditLogEntry backward compatibility ──────────────────────────────────

class TestAuditLogEntryExtended:
    def test_domain_defaults_none(self):
        entry = AuditLogEntry("test", "system", "target")
        assert entry.domain is None

    def test_to_dict_without_domain(self):
        entry = AuditLogEntry("test", "system", "target")
        d = entry.to_dict()
        assert "domain" not in d

    def test_to_dict_with_domain(self):
        entry = AuditLogEntry("test", "system", "target", domain="business")
        d = entry.to_dict()
        assert d["domain"] == "business"


# ── PriorityClassifier ────────────────────────────────────────────────────

class TestPriorityClassifier:
    def test_frontmatter_precedence(self):
        assert classify_priority("some urgent content", {"priority": "low"}) == "low"

    def test_frontmatter_invalid_falls_through(self):
        assert classify_priority("urgent task", {"priority": "invalid"}) == "urgent"

    def test_keyword_urgent(self):
        assert classify_priority("This is an urgent task with a deadline") == "urgent"

    def test_keyword_high(self):
        assert classify_priority("This is important financial data") == "high"

    def test_keyword_low(self):
        assert classify_priority("This is optional, low-priority cleanup") == "low"

    def test_default_normal(self):
        assert classify_priority("Do some regular work") == "normal"

    def test_empty_content(self):
        assert classify_priority("") == "normal"

    def test_no_frontmatter(self):
        assert classify_priority("regular task", None) == "normal"


# ── DomainClassifier ─────────────────────────────────────────────────────

class TestDomainClassifier:
    def test_frontmatter_precedence(self):
        assert classify_domain("invoice and personal stuff", {"domain": "business"}) == "business"

    def test_frontmatter_invalid_falls_through(self):
        assert classify_domain("invoice data", {"domain": "invalid"}) == "business"

    def test_business_keywords(self):
        assert classify_domain("Record the quarterly expense for vendor payment") == "business"

    def test_personal_keywords(self):
        assert classify_domain("Set a reminder for my personal appointment") == "personal"

    def test_cross_domain_detection(self):
        assert classify_domain("Schedule a personal appointment with the client vendor") == "cross-domain"

    def test_default_personal(self):
        assert classify_domain("Do something") == "personal"

    def test_empty_content(self):
        assert classify_domain("") == "personal"


# ── RetryQueueEntry ──────────────────────────────────────────────────────

class TestRetryQueueEntry:
    def test_to_markdown_roundtrip(self):
        entry = RetryQueueEntry(
            id="action_20260208_odoo_001",
            operation="create_expense",
            mcp_server="odoo",
            parameters={"amount": 500, "description": "Software"},
            approval_ref="approval_123",
            retry_count=1,
            max_retries=3,
            last_attempt=datetime(2026, 2, 8, 9, 10, 0),
            next_retry_after=datetime(2026, 2, 8, 9, 11, 0),
            error="Connection timeout",
            status="queued",
        )
        md = entry.to_markdown()
        parsed = RetryQueueEntry.from_markdown(md)

        assert parsed.id == entry.id
        assert parsed.operation == entry.operation
        assert parsed.mcp_server == entry.mcp_server
        assert parsed.parameters == entry.parameters
        assert parsed.retry_count == entry.retry_count
        assert parsed.max_retries == entry.max_retries
        assert parsed.error == entry.error
        assert parsed.status == entry.status

    def test_calculate_next_retry_backoff(self):
        entry = RetryQueueEntry(id="test", operation="op", mcp_server="s")
        entry.retry_count = 0
        entry.calculate_next_retry()
        # First retry: 30s backoff
        assert entry.next_retry_after is not None

        entry.retry_count = 1
        entry.calculate_next_retry()
        # Second retry: 60s backoff

        entry.retry_count = 2
        entry.calculate_next_retry()
        # Third retry: 120s backoff


# ── MCPServerStatus ──────────────────────────────────────────────────────

class TestMCPServerStatus:
    def test_default_healthy(self):
        status = MCPServerStatus(server_name="email")
        assert status.status == "healthy"

    def test_record_success_resets(self):
        status = MCPServerStatus(server_name="email", status="degraded", consecutive_failures=2)
        status.record_success()
        assert status.status == "healthy"
        assert status.consecutive_failures == 0
        assert status.last_success is not None

    def test_record_failure_degrades(self):
        status = MCPServerStatus(server_name="email")
        status.record_failure()
        assert status.status == "degraded"
        assert status.consecutive_failures == 1

    def test_three_failures_unavailable(self):
        status = MCPServerStatus(server_name="email")
        status.record_failure()
        status.record_failure()
        status.record_failure()
        assert status.status == "unavailable"
        assert status.consecutive_failures == 3

    def test_to_dict_from_dict_roundtrip(self):
        status = MCPServerStatus(
            server_name="odoo",
            status="degraded",
            failure_count=5,
            consecutive_failures=2,
            capabilities=["create_expense"],
        )
        status.record_success()
        d = status.to_dict()
        restored = MCPServerStatus.from_dict("odoo", d)
        assert restored.server_name == "odoo"
        assert restored.status == d["status"]
        assert restored.failure_count == d["failure_count"]


# ── AuditReportModel ──────────────────────────────────────────────────────

class TestAuditReportModel:
    def test_to_markdown_has_frontmatter(self):
        report = AuditReportModel(
            report_type="business_audit",
            period="2026-W06",
            data_sources=["logs", "accounting"],
            sections={"Financial Summary": {"Revenue": "$1000"}},
        )
        md = report.to_markdown()
        assert "---" in md
        assert "type: business_audit" in md
        assert "period: 2026-W06" in md
        assert "## Financial Summary" in md

    def test_to_markdown_ceo_briefing(self):
        report = AuditReportModel(
            report_type="ceo_briefing",
            period="2026-W06",
            data_sources=["logs"],
            sections={"Key Metrics": ["Revenue: $1000"]},
        )
        md = report.to_markdown()
        assert "# Executive Briefing" in md


# ── parse_frontmatter ─────────────────────────────────────────────────────

class TestParseFrontmatter:
    def test_parse_basic(self):
        content = "---\npriority: high\ndomain: business\n---\n# Title"
        fm = parse_frontmatter(content)
        assert fm["priority"] == "high"
        assert fm["domain"] == "business"

    def test_no_frontmatter(self):
        fm = parse_frontmatter("# Just a title")
        assert fm == {}

    def test_boolean_values(self):
        content = "---\nauto_approve: true\narchived: false\n---\n"
        fm = parse_frontmatter(content)
        assert fm["auto_approve"] is True
        assert fm["archived"] is False
