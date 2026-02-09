"""Data model for MCP server integration status"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MCPServerStatus:
    server_name: str
    status: str = "healthy"  # healthy, degraded, unavailable
    last_success: datetime | None = None
    failure_count: int = 0
    consecutive_failures: int = 0
    retry_queue_depth: int = 0
    capabilities: list[str] = field(default_factory=list)

    def record_success(self):
        """Record a successful operation — resets to healthy"""
        self.last_success = datetime.now()
        self.consecutive_failures = 0
        self.status = "healthy"

    def record_failure(self):
        """Record a failed operation — may degrade or mark unavailable"""
        self.failure_count += 1
        self.consecutive_failures += 1
        if self.consecutive_failures >= 3:
            self.status = "unavailable"
        elif self.consecutive_failures >= 1:
            self.status = "degraded"

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "failure_count": self.failure_count,
            "consecutive_failures": self.consecutive_failures,
            "retry_queue_depth": self.retry_queue_depth,
            "capabilities": self.capabilities,
        }

    @classmethod
    def from_dict(cls, server_name: str, data: dict) -> "MCPServerStatus":
        last_success = None
        if data.get("last_success"):
            try:
                last_success = datetime.fromisoformat(data["last_success"])
            except (ValueError, TypeError):
                pass

        return cls(
            server_name=server_name,
            status=data.get("status", "healthy"),
            last_success=last_success,
            failure_count=data.get("failure_count", 0),
            consecutive_failures=data.get("consecutive_failures", 0),
            retry_queue_depth=data.get("retry_queue_depth", 0),
            capabilities=data.get("capabilities", []),
        )
