"""Data model for retry queue entries persisted in vault Markdown"""
import json
import re
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RetryQueueEntry:
    id: str
    operation: str
    mcp_server: str
    parameters: dict = field(default_factory=dict)
    approval_ref: str = ""
    retry_count: int = 0
    max_retries: int = 3
    last_attempt: datetime | None = None
    next_retry_after: datetime | None = None
    error: str = ""
    status: str = "queued"  # queued, retrying, failed_permanent

    def calculate_next_retry(self) -> datetime:
        """Calculate next retry time using exponential backoff (30s, 60s, 120s)"""
        from datetime import timedelta
        backoff_seconds = 30 * (2 ** self.retry_count)
        now = datetime.now()
        self.next_retry_after = now + timedelta(seconds=backoff_seconds)
        return self.next_retry_after

    def to_markdown(self) -> str:
        """Serialize to Markdown section format"""
        params_json = json.dumps(self.parameters)
        last = self.last_attempt.isoformat() if self.last_attempt else "N/A"
        next_retry = self.next_retry_after.isoformat() if self.next_retry_after else "N/A"
        return (
            f"## Retry: {self.id}\n\n"
            f"- **Operation**: {self.operation}\n"
            f"- **MCP Server**: {self.mcp_server}\n"
            f"- **Parameters**: {params_json}\n"
            f"- **Approval Ref**: {self.approval_ref}\n"
            f"- **Retry Count**: {self.retry_count}/{self.max_retries}\n"
            f"- **Last Attempt**: {last}\n"
            f"- **Next Retry After**: {next_retry}\n"
            f"- **Error**: {self.error}\n"
            f"- **Status**: {self.status}\n"
            f"\n---\n"
        )

    @classmethod
    def from_markdown(cls, section: str) -> "RetryQueueEntry":
        """Deserialize from a Markdown section"""
        def extract(label: str) -> str:
            match = re.search(rf"\*\*{label}\*\*:\s*(.+)", section)
            return match.group(1).strip() if match else ""

        entry_id_match = re.search(r"## Retry:\s*(.+)", section)
        entry_id = entry_id_match.group(1).strip() if entry_id_match else ""

        retry_parts = extract("Retry Count").split("/")
        retry_count = int(retry_parts[0]) if retry_parts[0].isdigit() else 0
        max_retries = int(retry_parts[1]) if len(retry_parts) > 1 and retry_parts[1].isdigit() else 3

        params_str = extract("Parameters")
        try:
            parameters = json.loads(params_str)
        except (json.JSONDecodeError, TypeError):
            parameters = {}

        last_attempt_str = extract("Last Attempt")
        last_attempt = None
        if last_attempt_str and last_attempt_str != "N/A":
            try:
                last_attempt = datetime.fromisoformat(last_attempt_str)
            except ValueError:
                pass

        next_retry_str = extract("Next Retry After")
        next_retry_after = None
        if next_retry_str and next_retry_str != "N/A":
            try:
                next_retry_after = datetime.fromisoformat(next_retry_str)
            except ValueError:
                pass

        return cls(
            id=entry_id,
            operation=extract("Operation"),
            mcp_server=extract("MCP Server"),
            parameters=parameters,
            approval_ref=extract("Approval Ref"),
            retry_count=retry_count,
            max_retries=max_retries,
            last_attempt=last_attempt,
            next_retry_after=next_retry_after,
            error=extract("Error"),
            status=extract("Status") or "queued",
        )
