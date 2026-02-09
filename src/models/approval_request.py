"""Data model for HITL approval requests"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ApprovalRequest:
    action_type: str  # email_send, linkedin_post, etc.
    target: str
    parameters: dict[str, Any] = field(default_factory=dict)
    risk_level: str = "medium"  # low, medium, high
    auto_approve_eligible: bool = False
    mcp_server: str = "email_mcp"
    status: str = "pending"  # pending, approved, rejected, executed, failed
    created_at: datetime = field(default_factory=datetime.now)
    approval_source: str | None = None  # human, auto
    domain: str | None = None  # personal, business, cross-domain

    @property
    def id(self) -> str:
        return f"approval_{int(self.created_at.timestamp())}"

    @property
    def filename(self) -> str:
        return f"{self.id}.md"

    def to_frontmatter(self) -> str:
        lines = [
            "---",
            "type: approval_request",
            f"action: {self.action_type}",
            f"created: {self.created_at.isoformat()}",
            f"status: {self.status}",
            f"risk_level: {self.risk_level}",
            f"auto_approve_eligible: {str(self.auto_approve_eligible).lower()}",
            f"mcp_server: {self.mcp_server}",
        ]
        if self.domain is not None:
            lines.append(f"domain: {self.domain}")
        if self.approval_source is not None:
            lines.append(f"approval_source: {self.approval_source}")
        lines.append("---")
        return "\n".join(lines) + "\n"

    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "action_type": self.action_type,
            "target": self.target,
            "parameters": self.parameters,
            "risk_level": self.risk_level,
            "status": self.status,
            "mcp_server": self.mcp_server,
            "created_at": self.created_at.isoformat(),
        }
        if self.approval_source is not None:
            result["approval_source"] = self.approval_source
        if self.domain is not None:
            result["domain"] = self.domain
        return result
