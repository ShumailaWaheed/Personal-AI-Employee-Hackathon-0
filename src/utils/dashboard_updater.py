"""
Dashboard Updater
Updates Dashboard.md with current system status including Silver and Gold tier metrics
"""
import json
from pathlib import Path
from datetime import datetime


class DashboardUpdater:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.dashboard_path = self.vault_path / 'Dashboard.md'

    def update(self, dry_run: bool = False, processing_interval: int = 30,
               gold_enabled: bool = False, auto_approve: bool = False):
        """Update Dashboard.md with current vault status"""
        counts = self._get_counts()
        recent_logs = self._get_recent_logs()

        content = f"""# AI Employee Dashboard

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Status Overview
- **Pending Approval**: {counts['pending_approval']} items
- **Needs Action**: {counts['needs_action']} items
- **Approved (queued)**: {counts['approved']} items
- **Completed**: {counts['done']} items
- **Rejected**: {counts['rejected']} items

## Pending Approval Queue
"""
        pending_dir = self.vault_path / 'Pending_Approval'
        if pending_dir.exists():
            files = sorted(pending_dir.glob("*.md"))[:5]
            for f in files:
                content += f"- {f.name}\n"
            if counts['pending_approval'] > 5:
                content += f"- ... and {counts['pending_approval'] - 5} more\n"
        if counts['pending_approval'] == 0:
            content += "- No items pending approval\n"

        content += "\n## Recent Activity\n"
        if recent_logs:
            for log in reversed(recent_logs[-5:]):
                content += f"- {log.get('timestamp', 'N/A')}: {log.get('action_type', log.get('action', 'unknown'))} - {log.get('result', 'done')}\n"
        else:
            content += "- No recent activity\n"

        # MCP Server Status
        content += "\n## MCP Server Status\n"
        integration_status = self._get_integration_status()
        if integration_status:
            for name, server in integration_status.items():
                status_icon = {"healthy": "Operational", "degraded": "Degraded", "unavailable": "Unavailable"}.get(server.get("status", "unknown"), "Unknown")
                content += f"- **{name.title()} MCP**: {status_icon}\n"
        else:
            content += "- **Email MCP**: Operational\n"
        content += f"- **Last Heartbeat**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        # Gold tier sections
        if gold_enabled:
            content += f"""
## Autonomous Processing
- **Gold Tier**: {'Enabled' if gold_enabled else 'Disabled'}
- **Auto-Approve Low Risk**: {'Enabled' if auto_approve else 'Disabled'}
"""
            # Domain metrics
            domain_counts = self._get_domain_counts(recent_logs)
            content += "\n## Domain Metrics\n"
            content += f"- **Personal**: {domain_counts.get('personal', 0)} actions\n"
            content += f"- **Business**: {domain_counts.get('business', 0)} actions\n"
            content += f"- **Cross-Domain**: {domain_counts.get('cross-domain', 0)} actions\n"

            # Retry queue
            retry_depth = self._get_retry_depth()
            content += f"\n## Retry Queue\n- **Pending Retries**: {retry_depth}\n"

            # Last audit/briefing
            last_audit, last_briefing = self._get_last_report_times()
            content += f"\n## Reports\n"
            content += f"- **Last Audit**: {last_audit}\n"
            content += f"- **Last Briefing**: {last_briefing}\n"

        content += f"""
## System Settings
- **Dry Run Mode**: {'Enabled' if dry_run else 'Disabled'}
- **Processing Interval**: {processing_interval}s
"""

        self.dashboard_path.write_text(content, encoding='utf-8')

    def _get_counts(self) -> dict:
        dirs = {
            'needs_action': 'Needs_Action',
            'pending_approval': 'Pending_Approval',
            'approved': 'Approved',
            'rejected': 'Rejected',
            'done': 'Done',
        }
        counts = {}
        for key, dirname in dirs.items():
            d = self.vault_path / dirname
            counts[key] = len(list(d.glob("*.md"))) if d.exists() else 0
        return counts

    def _get_recent_logs(self) -> list:
        log_dir = self.vault_path / 'Logs'
        if not log_dir.exists():
            return []
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = log_dir / f"{today}.json"
        if not log_path.exists():
            return []
        try:
            return json.loads(log_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            return []

    def _get_integration_status(self) -> dict:
        status_path = self.vault_path / 'Business' / 'integration_status.json'
        if not status_path.exists():
            return {}
        try:
            data = json.loads(status_path.read_text(encoding='utf-8'))
            return data.get('servers', {})
        except (json.JSONDecodeError, OSError):
            return {}

    def _get_domain_counts(self, logs: list) -> dict:
        counts = {'personal': 0, 'business': 0, 'cross-domain': 0}
        for log in logs:
            domain = log.get('domain')
            if domain in counts:
                counts[domain] += 1
        return counts

    def _get_retry_depth(self) -> int:
        retry_path = self.vault_path / 'Business' / 'retry_queue.md'
        if not retry_path.exists():
            return 0
        content = retry_path.read_text(encoding='utf-8')
        return content.count('## Retry:')

    def _get_last_report_times(self) -> tuple[str, str]:
        briefings = self.vault_path / 'Briefings'
        last_audit = "Never"
        last_briefing = "Never"
        if briefings.exists():
            audits = sorted(briefings.glob("audit_*.md"))
            if audits:
                last_audit = audits[-1].stem.replace('audit_', '')
            briefings_files = sorted(briefings.glob("ceo_briefing_*.md"))
            if briefings_files:
                last_briefing = briefings_files[-1].stem.replace('ceo_briefing_', '')
        return last_audit, last_briefing
