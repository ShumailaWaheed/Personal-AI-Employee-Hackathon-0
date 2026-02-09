"""
Approval Formatter
Creates properly formatted approval request files following constitution guidelines.
Gold tier adds auto-approval for low-risk actions when opted in.
"""
from pathlib import Path
from datetime import datetime

from models.approval_request import ApprovalRequest


class ApprovalFormatter:
    def __init__(self, vault_path: str, auto_approve_low_risk: bool = False):
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.auto_approve_low_risk = auto_approve_low_risk

    def should_auto_approve(self, request: ApprovalRequest) -> bool:
        """Check if a request should be auto-approved (Gold tier)"""
        if not self.auto_approve_low_risk:
            return False
        if request.risk_level != 'low':
            return False
        if not request.auto_approve_eligible:
            return False
        if request.domain == 'cross-domain':
            return False
        return True

    def create_approval_file(self, request: ApprovalRequest, plan_summary: str = "") -> Path:
        """Create an approval request markdown file in /Pending_Approval"""
        filepath = self.pending_approval / request.filename

        content = request.to_frontmatter()
        content += f"""
# Approval Request: {request.action_type}

## Proposed Action
**Type**: {request.action_type}
**Target**: {request.target}
**Risk Level**: {request.risk_level}

## Parameters
"""
        for key, value in request.parameters.items():
            content += f"- **{key}**: {value}\n"

        if plan_summary:
            content += f"\n## Plan Summary\n{plan_summary}\n"

        content += f"""
## Risk Assessment
Risk level: **{request.risk_level}**. This action involves external communication that may represent the organization.

## Approval Instructions
- Move this file to `/Approved/` to execute the action
- Move this file to `/Rejected/` to cancel
- The action will be executed via MCP server: **{request.mcp_server}**
"""
        filepath.write_text(content, encoding='utf-8')
        return filepath
