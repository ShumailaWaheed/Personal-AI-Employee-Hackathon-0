"""Data model for audit reports and executive briefings"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AuditReportModel:
    report_type: str  # business_audit, ceo_briefing
    period: str  # e.g. "2026-W06"
    generated: datetime = field(default_factory=datetime.now)
    data_sources: list[str] = field(default_factory=list)
    missing_sources: list[str] = field(default_factory=list)
    sections: dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Render report as Markdown with frontmatter"""
        sources_yaml = "\n".join(f"  - {s}" for s in self.data_sources)
        missing_yaml = "\n".join(f"  - {s}" for s in self.missing_sources) if self.missing_sources else "  []"

        lines = [
            "---",
            f"type: {self.report_type}",
            f"period: {self.period}",
            f"generated: {self.generated.isoformat()}",
            "data_sources:",
            sources_yaml,
            "missing_sources:",
            missing_yaml,
            "---",
            "",
        ]

        if self.report_type == "business_audit":
            lines.append(f"# Business Audit Report — {self.period}")
        else:
            lines.append(f"# Executive Briefing — {self.period}")
        lines.append("")

        for section_title, section_content in self.sections.items():
            lines.append(f"## {section_title}")
            lines.append("")
            if isinstance(section_content, list):
                for item in section_content:
                    lines.append(f"- {item}")
            elif isinstance(section_content, dict):
                for key, value in section_content.items():
                    lines.append(f"- **{key}**: {value}")
            else:
                lines.append(str(section_content))
            lines.append("")

        return "\n".join(lines)
