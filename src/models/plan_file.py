"""Data model for plan files"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class PlanFile:
    title: str
    description: str
    steps: list[str] = field(default_factory=list)
    status: str = "draft"  # draft, pending_approval, approved, in_progress, completed, failed
    dependencies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    filepath: Path | None = None

    @property
    def id(self) -> str:
        return f"plan_{int(self.created_at.timestamp())}"

    @property
    def filename(self) -> str:
        return f"PLAN_{self.created_at.strftime('%Y%m%d_%H%M%S')}_{self.title.replace(' ', '_')[:30]}.md"

    def to_markdown(self) -> str:
        frontmatter = (
            f"---\n"
            f"created: {self.created_at.isoformat()}\n"
            f"status: {self.status}\n"
            f"priority: medium\n"
            f"---\n\n"
        )
        body = f"# Plan: {self.title}\n\n## Objective\n{self.description}\n\n## Action Steps\n"
        for i, step in enumerate(self.steps, 1):
            body += f"- [ ] Step {i}: {step}\n"
        if self.dependencies:
            body += "\n## Dependencies\n"
            for dep in self.dependencies:
                body += f"- {dep}\n"
        return frontmatter + body
