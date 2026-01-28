"""
Action Item Representation
Defines the structure and behavior of action items in the AI employee system
"""
from pathlib import Path
from datetime import datetime
from typing import Optional


class ActionItem:
    def __init__(
        self,
        file_path: Path,
        title: str = "",
        content: str = "",
        status: str = "inbox",
        created_at: Optional[datetime] = None,
        processed_at: Optional[datetime] = None
    ):
        self.file_path = file_path
        self.title = title or file_path.stem
        self.content = content
        self.status = status
        self.created_at = created_at or datetime.now()
        self.processed_at = processed_at

    @classmethod
    def from_file(cls, file_path: Path) -> 'ActionItem':
        """Create an ActionItem from a file path"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title from the first heading if available
        title = cls._extract_title(content, file_path.stem)

        # Determine status based on directory
        if "Inbox" in str(file_path):
            status = "inbox"
        elif "Needs_Action" in str(file_path):
            status = "needs_action"
        elif "Done" in str(file_path):
            status = "done"
        else:
            status = "unknown"

        return cls(
            file_path=file_path,
            title=title,
            content=content,
            status=status
        )

    @staticmethod
    def _extract_title(content: str, default_title: str) -> str:
        """Extract title from content (first heading or first line)"""
        lines = content.strip().split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
            elif line.startswith('##'):
                return line.lstrip('# ').strip()

        # If no heading found, try first non-empty line
        for line in lines:
            line = line.strip()
            if line and not line.startswith('---'):
                return line[:50] + '...' if len(line) > 50 else line

        return default_title

    def to_dict(self) -> dict:
        """Convert ActionItem to dictionary representation"""
        return {
            'id': str(self.file_path),
            'title': self.title,
            'content': self.content[:100] + '...' if len(self.content) > 100 else self.content,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

    def update_status(self, new_status: str):
        """Update the status of the action item"""
        old_status = self.status
        self.status = new_status

        if new_status == 'done' and self.processed_at is None:
            self.processed_at = datetime.now()

    def save(self):
        """Save the action item back to its file (not implemented in Bronze tier)"""
        # In Bronze tier, we don't modify files directly, just move them between directories
        pass

    def __repr__(self):
        return f"ActionItem(title='{self.title}', status='{self.status}', path='{self.file_path}')"