"""Data model for action files in the vault"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class ActionFile:
    filename: str
    filepath: Path
    action_type: str
    content: str
    priority: str = "normal"  # urgent, high, normal, low
    status: str = "pending"  # pending, processing, needs_approval, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    domain: str | None = None  # personal, business, cross-domain
    processor: str | None = None  # gold_processor, silver_processor, etc.

    @property
    def id(self) -> str:
        return self.filename.replace(".md", "")

    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "filename": self.filename,
            "filepath": str(self.filepath),
            "action_type": self.action_type,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
        if self.domain is not None:
            result["domain"] = self.domain
        if self.processor is not None:
            result["processor"] = self.processor
        return result
