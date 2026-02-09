"""
Comprehensive test suite for Silver Tier Personal AI Employee
Tests backward compatibility, HITL workflow, MCP integration, audit logging,
social media automation, and dashboard updates.
"""
import sys
import os
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

# Set up path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest


@pytest.fixture
def vault(tmp_path):
    """Create a temporary vault with Silver tier directory structure"""
    dirs = ['Inbox', 'Needs_Action', 'Pending_Approval', 'Approved',
            'Rejected', 'Done', 'Logs', 'Plans']
    for d in dirs:
        (tmp_path / d).mkdir()

    # Create Company_Handbook.md
    (tmp_path / 'Company_Handbook.md').write_text(
        "# Company Handbook\n\nWe value innovation and growth.\n",
        encoding='utf-8'
    )
    return tmp_path


@pytest.fixture
def config(vault):
    """Create test config"""
    return {
        'VAULT_PATH': str(vault),
        'CHECK_INTERVAL': 1,
        'LOG_LEVEL': 'INFO',
        'DRY_RUN': True,
        'PROCESSING_INTERVAL': 1,
    }


# ---- Bronze Tier Backward Compatibility ----

class TestBronzeCompatibility:
    def test_vault_processor_initializes(self, vault):
        from processors.vault_processor import VaultProcessor
        vp = VaultProcessor(str(vault))
        assert vp.inbox.exists()
        assert vp.needs_action.exists()
        assert vp.done.exists()

    def test_vault_stats(self, vault):
        from processors.vault_processor import VaultProcessor
        (vault / 'Needs_Action' / 'test_task.md').write_text("# Test", encoding='utf-8')
        vp = VaultProcessor(str(vault))
        stats = vp.get_vault_stats()
        assert stats['needs_action_count'] == 1

    def test_dashboard_update(self, vault):
        from processors.vault_processor import VaultProcessor
        vp = VaultProcessor(str(vault))
        vp.update_dashboard()
        dashboard = vault / 'Dashboard.md'
        assert dashboard.exists()
        content = dashboard.read_text(encoding='utf-8')
        assert 'Dashboard' in content

    def test_action_item_model(self, vault):
        from processors.action_item import ActionItem
        filepath = vault / 'Needs_Action' / 'test.md'
        filepath.write_text("# Test Task\n\nDo something.", encoding='utf-8')
        item = ActionItem.from_file(filepath)
        assert item.title == 'Test Task'
        assert item.status == 'needs_action'


# ---- Data Models ----

class TestDataModels:
    def test_watcher_input(self):
        from models.watcher_input import WatcherInput
        wi = WatcherInput(source_type='gmail', content='New email', source_id='msg123')
        assert wi.source_type == 'gmail'
        assert 'gmail' in wi.id

    def test_approval_request(self):
        from models.approval_request import ApprovalRequest
        req = ApprovalRequest(action_type='email_send', target='test@example.com')
        assert req.status == 'pending'
        assert 'approval_' in req.id
        frontmatter = req.to_frontmatter()
        assert 'type: approval_request' in frontmatter

    def test_audit_log_entry(self):
        from models.audit_log_entry import AuditLogEntry
        entry = AuditLogEntry(action_type='email_send', actor='system', target='test')
        d = entry.to_dict()
        assert d['action_type'] == 'email_send'
        assert 'timestamp' in d

    def test_plan_file(self):
        from models.plan_file import PlanFile
        plan = PlanFile(title='Test Plan', description='Do stuff', steps=['Step 1', 'Step 2'])
        md = plan.to_markdown()
        assert '# Plan: Test Plan' in md
        assert 'Step 1' in md


# ---- Sensitive Action Detection ----

class TestSensitiveActionDetection:
    def test_email_is_sensitive(self):
        from utils.sensitive_action_detector import requires_approval
        assert requires_approval('Please send an email to the client') is True

    def test_linkedin_is_sensitive(self):
        from utils.sensitive_action_detector import requires_approval
        assert requires_approval('Post a LinkedIn update') is True

    def test_payment_is_sensitive(self):
        from utils.sensitive_action_detector import requires_approval
        assert requires_approval('Make a payment of $500') is True

    def test_read_is_not_sensitive(self):
        from utils.sensitive_action_detector import requires_approval
        assert requires_approval('Read the project status report') is False

    def test_action_type_detection(self):
        from utils.sensitive_action_detector import detect_action_type
        assert detect_action_type('send email to client') == 'email_send'
        assert detect_action_type('post on LinkedIn') == 'linkedin_post'
        assert detect_action_type('payment transfer') == 'financial_action'

    def test_risk_assessment(self):
        from utils.sensitive_action_detector import assess_risk
        assert assess_risk('make a payment') == 'high'
        assert assess_risk('send an email') == 'medium'
        assert assess_risk('update document') == 'low'


# ---- PII Sanitization ----

class TestLogSanitizer:
    def test_email_redacted(self):
        from utils.log_sanitizer import sanitize_entry
        entry = {'target': 'user@example.com'}
        sanitized = sanitize_entry(entry)
        assert 'user@example.com' not in str(sanitized)
        assert 'REDACTED' in str(sanitized)

    def test_password_redacted(self):
        from utils.log_sanitizer import sanitize_entry
        entry = {'parameters': {'password': 'secret123'}}
        sanitized = sanitize_entry(entry)
        assert 'secret123' not in str(sanitized)

    def test_token_redacted(self):
        from utils.log_sanitizer import sanitize_entry
        entry = {'parameters': {'token': 'abc123xyz'}}
        sanitized = sanitize_entry(entry)
        assert 'abc123xyz' not in str(sanitized)

    def test_non_sensitive_preserved(self):
        from utils.log_sanitizer import sanitize_entry
        entry = {'action_type': 'email_send', 'result': 'success'}
        sanitized = sanitize_entry(entry)
        assert sanitized['action_type'] == 'email_send'
        assert sanitized['result'] == 'success'


# ---- Audit Logging ----

class TestAuditLogging:
    def test_audit_log_created(self, vault):
        from utils.audit_logger import AuditLogger
        from models.audit_log_entry import AuditLogEntry
        logger = AuditLogger(str(vault))
        entry = AuditLogEntry(action_type='test', actor='system', target='test')
        logger.log(entry)
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = vault / 'Logs' / f'{today}.json'
        assert log_path.exists()
        entries = json.loads(log_path.read_text(encoding='utf-8'))
        assert len(entries) == 1
        assert entries[0]['action_type'] == 'test'

    def test_audit_log_appends(self, vault):
        from utils.audit_logger import AuditLogger
        from models.audit_log_entry import AuditLogEntry
        logger = AuditLogger(str(vault))
        logger.log(AuditLogEntry(action_type='first', actor='system', target='t'))
        logger.log(AuditLogEntry(action_type='second', actor='system', target='t'))
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = vault / 'Logs' / f'{today}.json'
        entries = json.loads(log_path.read_text(encoding='utf-8'))
        assert len(entries) == 2


# ---- Dashboard Updates ----

class TestDashboardUpdater:
    def test_dashboard_shows_counts(self, vault):
        from utils.dashboard_updater import DashboardUpdater
        (vault / 'Needs_Action' / 'task1.md').write_text("# Task 1", encoding='utf-8')
        (vault / 'Pending_Approval' / 'approval1.md').write_text("# Approval", encoding='utf-8')
        updater = DashboardUpdater(str(vault))
        updater.update()
        content = (vault / 'Dashboard.md').read_text(encoding='utf-8')
        assert '1 items' in content or '**Pending Approval**: 1' in content
        assert 'MCP Server Status' in content


# ---- HITL Approval Workflow ----

class TestHITLWorkflow:
    def test_sensitive_action_routed_to_approval(self, vault, config):
        from processors.silver_processor import SilverProcessor
        (vault / 'Needs_Action' / 'send_email_task.md').write_text(
            "# Send Email to Client\n\nPlease send an email to the client about the proposal.",
            encoding='utf-8'
        )
        processor = SilverProcessor(str(vault), config)
        processor.process_all()
        # File should be in Done (original) and approval in Pending_Approval
        assert len(list((vault / 'Done').glob('*.md'))) >= 1
        assert len(list((vault / 'Pending_Approval').glob('*.md'))) >= 1

    def test_non_sensitive_processed_directly(self, vault, config):
        from processors.silver_processor import SilverProcessor
        (vault / 'Needs_Action' / 'update_report.md').write_text(
            "# Update Report\n\nUpdate the quarterly status report with new figures.",
            encoding='utf-8'
        )
        processor = SilverProcessor(str(vault), config)
        processor.process_all()
        # No approval requests for non-sensitive actions
        assert len(list((vault / 'Pending_Approval').glob('*.md'))) == 0

    def test_approved_action_executes(self, vault, config):
        from processors.silver_processor import SilverProcessor
        (vault / 'Approved' / 'approval_test.md').write_text(
            "---\ntype: approval_request\naction: email_send\n---\n# Test Approval\nSend email.",
            encoding='utf-8'
        )
        processor = SilverProcessor(str(vault), config)
        processor.process_all()
        assert len(list((vault / 'Done').glob('approval_test.md'))) == 1
        assert len(list((vault / 'Approved').glob('*.md'))) == 0


# ---- Social Media Automation ----

class TestSocialMedia:
    def test_post_generation(self, vault):
        from social.linkedin_post_generator import LinkedInPostGenerator
        gen = LinkedInPostGenerator(str(vault))
        post = gen.generate_post('AI Innovation')
        assert 'content' in post
        assert len(post['content']) > 0
        assert len(post['hashtags']) > 0

    def test_rate_limiter(self, vault):
        from social.rate_limiter import RateLimiter
        rl = RateLimiter(str(vault), max_posts_per_day=2)
        assert rl.can_post() is True
        rl.record_post()
        assert rl.remaining_posts() == 1
        rl.record_post()
        assert rl.can_post() is False

    def test_linkedin_approval_flow(self, vault):
        from workflows.linkedin_approval_flow import LinkedInApprovalFlow
        flow = LinkedInApprovalFlow(str(vault))
        path = flow.create_post_for_approval('Test Topic')
        assert path is not None
        assert path.exists()
        content = path.read_text(encoding='utf-8')
        assert 'linkedin_post' in content


# ---- MCP Client ----

class TestMCPClient:
    def test_mcp_client_initializes(self):
        from utils.mcp_client import MCPClient
        client = MCPClient()
        assert client.server_script is not None


# ---- Log Manager ----

class TestLogManager:
    def test_log_summary(self, vault):
        from utils.log_manager import LogManager
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = vault / 'Logs' / f'{today}.json'
        log_path.write_text(json.dumps([
            {"action_type": "test", "result": "success", "timestamp": datetime.now().isoformat()},
            {"action_type": "test", "result": "failure", "timestamp": datetime.now().isoformat()},
        ]), encoding='utf-8')
        mgr = LogManager(str(vault))
        summary = mgr.get_log_summary()
        assert summary['total_entries'] == 2
        assert summary['success_count'] == 1
        assert summary['failure_count'] == 1


# ---- Security Validation ----

class TestSecurity:
    def test_no_credentials_in_code(self):
        """Verify no hardcoded credentials in source files"""
        src_dir = Path(__file__).parent.parent / 'src'
        sensitive_patterns = ['api_key=', 'secret_key=']
        # Files that legitimately reference credential key names (sanitizers, config)
        allowed_files = {'log_sanitizer.py', 'config_loader.py', 'settings.py'}
        for py_file in src_dir.rglob('*.py'):
            if py_file.name in allowed_files:
                continue
            content = py_file.read_text(encoding='utf-8').lower()
            for pattern in sensitive_patterns:
                lines_with_pattern = [
                    line for line in content.split('\n')
                    if pattern in line and 'getenv' not in line and 'os.environ' not in line
                ]
                assert len(lines_with_pattern) == 0, \
                    f"Potential credential found in {py_file}: {pattern}"

    def test_gitignore_has_env(self):
        """Verify .gitignore excludes .env"""
        gitignore = Path(__file__).parent.parent / '.gitignore'
        assert gitignore.exists()
        content = gitignore.read_text(encoding='utf-8')
        assert '.env' in content
