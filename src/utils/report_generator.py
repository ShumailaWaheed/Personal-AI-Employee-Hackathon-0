"""
Report Generator
Generates weekly audit reports and executive briefings from vault data.
"""
import json
import logging
from pathlib import Path
from datetime import datetime

from models.audit_report import AuditReportModel

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates audit reports and executive briefings"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.briefings_dir = self.vault_path / 'Briefings'
        self.briefings_dir.mkdir(parents=True, exist_ok=True)

    def generate_audit_report(self, period: str | None = None) -> Path:
        """Generate a business audit report aggregating all available data sources"""
        now = datetime.now()
        if not period:
            period = f"{now.year}-W{now.isocalendar().week:02d}"

        data_sources = []
        missing_sources = []
        sections = {}

        # 1. Operational Metrics from /Logs/
        log_metrics = self._collect_log_metrics()
        if log_metrics:
            sections["Operational Metrics"] = log_metrics
            data_sources.append("logs")
        else:
            missing_sources.append("logs")
            sections["Operational Metrics"] = "[DATA UNAVAILABLE: logs]"

        # 2. Financial Summary from /Business/Accounting/
        financial = self._collect_financial_data()
        if financial:
            sections["Financial Summary"] = financial
            data_sources.append("accounting")
        else:
            missing_sources.append("accounting")
            sections["Financial Summary"] = "[DATA UNAVAILABLE: accounting]"

        # 3. Social Media Performance from /Business/Social/
        social = self._collect_social_data()
        if social:
            sections["Social Media Performance"] = social
            data_sources.append("social")
        else:
            missing_sources.append("social")
            sections["Social Media Performance"] = "[DATA UNAVAILABLE: social]"

        # 4. Action Item Statistics from vault directories
        vault_stats = self._collect_vault_stats()
        sections["Action Item Statistics"] = vault_stats
        data_sources.append("vault_activity")

        # 5. Integration Health from /Business/integration_status.json
        integration = self._collect_integration_health()
        if integration:
            sections["Integration Health"] = integration
            data_sources.append("integration_status")
        else:
            missing_sources.append("integration_status")
            sections["Integration Health"] = "[DATA UNAVAILABLE: integration_status]"

        report = AuditReportModel(
            report_type="business_audit",
            period=period,
            generated=now,
            data_sources=data_sources,
            missing_sources=missing_sources,
            sections=sections,
        )

        filename = f"audit_{now.strftime('%Y-%m-%d')}.md"
        report_path = self.briefings_dir / filename
        report_path.write_text(report.to_markdown(), encoding='utf-8')

        logger.info(f"Generated audit report: {filename}")
        return report_path

    def generate_executive_briefing(self, audit_path: Path) -> Path:
        """Generate executive briefing from audit report data"""
        now = datetime.now()
        period = f"{now.year}-W{now.isocalendar().week:02d}"

        audit_content = audit_path.read_text(encoding='utf-8') if audit_path.exists() else ""

        # Extract key metrics
        key_metrics = self._extract_key_metrics(audit_content)
        highlights = self._extract_highlights(audit_content)
        concerns = self._extract_concerns(audit_content)
        recommended = self._generate_recommendations(audit_content)

        sections = {
            "Key Metrics": key_metrics,
            "Highlights": highlights,
            "Concerns": concerns,
            "Recommended Actions": recommended,
        }

        report = AuditReportModel(
            report_type="ceo_briefing",
            period=period,
            generated=now,
            data_sources=["audit_report"],
            sections=sections,
        )

        filename = f"ceo_briefing_{now.strftime('%Y-%m-%d')}.md"
        briefing_path = self.briefings_dir / filename
        briefing_path.write_text(report.to_markdown(), encoding='utf-8')

        logger.info(f"Generated executive briefing: {filename}")
        return briefing_path

    # ── Data collection helpers ──────────────────────────────────────

    def _collect_log_metrics(self) -> dict | None:
        log_dir = self.vault_path / 'Logs'
        if not log_dir.exists():
            return None

        total_actions = 0
        successes = 0
        failures = 0
        action_types: dict[str, int] = {}

        for log_file in sorted(log_dir.glob("*.json")):
            try:
                entries = json.loads(log_file.read_text(encoding='utf-8'))
                for entry in entries:
                    total_actions += 1
                    result = entry.get('result', 'success')
                    if result == 'success':
                        successes += 1
                    else:
                        failures += 1
                    atype = entry.get('action_type', entry.get('action', 'unknown'))
                    action_types[atype] = action_types.get(atype, 0) + 1
            except (json.JSONDecodeError, OSError):
                continue

        if total_actions == 0:
            return None

        rate = f"{(successes / total_actions * 100):.0f}%" if total_actions else "N/A"
        metrics = {
            "Total Actions": total_actions,
            "Successes": successes,
            "Failures": failures,
            "Success Rate": rate,
        }
        for atype, count in sorted(action_types.items(), key=lambda x: -x[1])[:5]:
            metrics[f"Type: {atype}"] = count
        return metrics

    def _collect_financial_data(self) -> dict | None:
        accounting_dir = self.vault_path / 'Business' / 'Accounting'
        if not accounting_dir.exists():
            return None
        files = list(accounting_dir.glob("*.md"))
        if not files:
            return None
        return {
            "Total Records": len(files),
            "Expenses": len([f for f in files if f.name.startswith('expense_')]),
            "Invoices": len([f for f in files if f.name.startswith('invoice_')]),
        }

    def _collect_social_data(self) -> dict | None:
        social_dir = self.vault_path / 'Business' / 'Social'
        if not social_dir.exists():
            return None
        files = list(social_dir.glob("*.md"))
        if not files:
            return None
        return {"Total Posts": len(files)}

    def _collect_vault_stats(self) -> dict:
        stats = {}
        for dirname in ['Needs_Action', 'Pending_Approval', 'Done']:
            d = self.vault_path / dirname
            stats[dirname] = len(list(d.glob("*.md"))) if d.exists() else 0
        return stats

    def _collect_integration_health(self) -> dict | None:
        status_path = self.vault_path / 'Business' / 'integration_status.json'
        if not status_path.exists():
            return None
        try:
            data = json.loads(status_path.read_text(encoding='utf-8'))
            servers = data.get('servers', {})
            return {name: info.get('status', 'unknown') for name, info in servers.items()}
        except (json.JSONDecodeError, OSError):
            return None

    # ── Briefing extraction helpers ──────────────────────────────────

    def _extract_key_metrics(self, audit_content: str) -> list:
        metrics = []
        if 'Total Actions' in audit_content:
            for line in audit_content.split('\n'):
                if 'Total Actions' in line or 'Success Rate' in line:
                    metrics.append(line.strip().lstrip('- '))
        if not metrics:
            metrics.append("No activity data available for this period")
        return metrics[:5]

    def _extract_highlights(self, audit_content: str) -> list:
        if 'Success Rate' in audit_content and '100%' in audit_content:
            return ["100% success rate on all operations"]
        if 'Success Rate' in audit_content:
            return ["Operations running with mixed results — review failures"]
        return ["No operational data to highlight"]

    def _extract_concerns(self, audit_content: str) -> list:
        concerns = []
        if 'Failures' in audit_content:
            for line in audit_content.split('\n'):
                if 'Failures' in line and '0' not in line.split('Failures')[-1][:5]:
                    concerns.append("Some operations experienced failures — review logs")
                    break
        if 'DATA UNAVAILABLE' in audit_content:
            concerns.append("Some data sources were unavailable during report generation")
        if not concerns:
            concerns.append("No concerns identified")
        return concerns

    def _generate_recommendations(self, audit_content: str) -> list:
        recs = []
        if 'DATA UNAVAILABLE' in audit_content:
            recs.append("Configure missing integrations to improve report coverage")
        if 'unavailable' in audit_content.lower():
            recs.append("Investigate unavailable MCP servers")
        if not recs:
            recs.append("Continue normal operations")
        return recs[:3]
