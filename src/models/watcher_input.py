"""Data model for watcher inputs from external sources"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class WatcherInput:
    source_type: str  # gmail, whatsapp, linkedin, filesystem
    content: str
    source_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    processed: bool = False
    action_required: bool = True

    @property
    def id(self) -> str:
        return f"{self.source_type}_{int(self.timestamp.timestamp())}"
