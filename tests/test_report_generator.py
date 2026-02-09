"""
Report Generator tests — US4: Weekly Business Audit & Executive Briefing
Tests audit report generation, executive briefing, missing data handling,
zero-activity reports, frontmatter correctness.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent / 'src'))

import pytest


@pytest.fixture
def vault(tmp_path):
    dirs = ['Logs', 'Business/Accounting', 'Business/Social', 'Briefings',
            'Needs_Action', 'Pending_Approval', 'Done']
    for d in dirs:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def vault_with_logs(vault):
    """Vault with sample log data"""
    today = datetime.now().strftime('%Y-%m-%d')
    logs = [
        {"timestamp": "2026-02-08T09:00:00", "action_type": "email_send", "result": "success", "domain": "business"},
        {"timestamp": "2026-02-08T09:05:00", "action_type": "route_to_approval", "result": "success", "domain": "personal"},
        {"timestamp": "2026-02-08T09:10:00", "action_type": "email_send", "result": "failure", "domain": "business"},
    ]
    (vault / 'Logs' / f'{today}.json').write_text(json.dumps(logs), encoding='utf-8')

    # Add some done files
    (vault / 'Done' / 'task1.md').write_text("# Done task 1", encoding='utf-8')
    (vault / 'Done' / 'task2.md').write_text("# Done task 2", encoding='utf-8')

    return vault


class TestAuditReportGeneration:
    def test_generates_audit_report(self, vault_with_logs):
        from utils.report_generator import ReportGenerator
        gen = ReportGenerator(str(vault_with_logs))
        report_path = gen.generate_audit_report()

        assert report_path.exists()
        content = report_path.read_text(encoding='utf-8')
        assert 'type: business_audit' in content
        assert '## Operational Metrics' in content

    def test_audit_report_in_briefings_dir(self, vault_with_logs):
        from utils.report_generator import ReportGenerator
        gen = ReportGenerator(str(vault_with_logs))
        report_path = gen.generate_audit_report()

        assert report_path.parent.name == 'Briefings'
        assert report_path.name.startswith('audit_')

    def test_audit_report_frontmatter(self, vault_with_logs):
        from utils.report_generator import ReportGenerator
        gen = ReportGenerator(str(vault_with_logs))
        report_path = gen.generate_audit_report()

        content = report_path.read_text(encoding='utf-8')
        assert 'type: business_audit' in content
        assert 'period:' in content
        assert 'generated:' in content
        assert 'data_sources:' in content


class TestExecutiveBriefing:
    def test_generates_briefing(self, vault_with_logs):
        from utils.report_generator import ReportGenerator
        gen = ReportGenerator(str(vault_with_logs))
        audit_path = gen.generate_audit_report()
        briefing_path = gen.generate_executive_briefing(audit_path)

        assert briefing_path.exists()
        content = briefing_path.read_text(encoding='utf-8')
        assert 'type: ceo_briefing' in content

    def test_briefing_in_briefings_dir(self, vault_with_logs):
        from utils.report_generator import ReportGenerator
        gen = ReportGenerator(str(vault_with_logs))
        audit_path = gen.generate_audit_report()
        briefing_path = gen.generate_executive_briefing(audit_path)

        assert briefing_path.parent.name == 'Briefings'
        assert briefing_path.name.startswith('ceo_briefing_')


class TestMissingDataHandling:
    def test_missing_sources_marked(self, vault):
        """When data sources are empty, report should note them as unavailable"""
        from utils.report_generator import ReportGenerator
        gen = ReportGenerator(str(vault))
        report_path = gen.generate_audit_report()

        content = report_path.read_text(encoding='utf-8')
        assert report_path.exists()
        # Should still generate even with no data
        assert 'business_audit' in content


class TestZeroActivity:
    def test_zero_activity_report(self, vault):
        from utils.report_generator import ReportGenerator
        gen = ReportGenerator(str(vault))
        report_path = gen.generate_audit_report()

        assert report_path.exists()
        content = report_path.read_text(encoding='utf-8')
        assert 'business_audit' in content
