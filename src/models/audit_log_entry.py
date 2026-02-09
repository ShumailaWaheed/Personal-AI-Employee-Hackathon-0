"""Data model for structured audit log entries"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AuditLogEntry:
    action_type: str
    actor: str  # system, user
    target: str
    parameters: dict[str, Any] = field(default_factory=dict)
    approval_status: str = "direct"  # approved, rejected, auto_approved, direct
    result: str = "success"  # success, failure
    execution_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    domain: str | None = None  # personal, business, cross-domain

    def to_dict(self) -> dict:
        result = {
            "timestamp": self.timestamp.isoformat(),
            "action_type": self.action_type,
            "actor": self.actor,
            "target": self.target,
            "parameters": self.parameters,
            "approval_status": self.approval_status,
            "result": self.result,
            "execution_time_ms": self.execution_time_ms,
        }
        if self.domain is not None:
            result["domain"] = self.domain
        return result
