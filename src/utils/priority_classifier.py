"""
Priority Classifier
Determines action item priority from frontmatter metadata or keyword inference
"""
import re


# Priority keyword sets
URGENT_KEYWORDS = ['urgent', 'deadline', 'asap', 'critical', 'immediately', 'emergency']
HIGH_KEYWORDS = ['important', 'financial', 'high priority', 'time-sensitive', 'revenue']
LOW_KEYWORDS = ['low-priority', 'optional', 'when possible', 'nice to have', 'backlog']

VALID_PRIORITIES = ('urgent', 'high', 'normal', 'low')


def classify_priority(content: str, frontmatter: dict | None = None) -> str:
    """Classify priority from frontmatter field or keyword inference.

    Priority precedence:
    1. Frontmatter `priority:` field (if valid)
    2. Keyword inference from content
    3. Default: "normal"
    """
    # Check frontmatter first
    if frontmatter and 'priority' in frontmatter:
        fm_priority = str(frontmatter['priority']).lower().strip()
        if fm_priority in VALID_PRIORITIES:
            return fm_priority

    # Keyword inference fallback
    content_lower = content.lower()

    if any(kw in content_lower for kw in URGENT_KEYWORDS):
        return 'urgent'
    if any(kw in content_lower for kw in HIGH_KEYWORDS):
        return 'high'
    if any(kw in content_lower for kw in LOW_KEYWORDS):
        return 'low'

    return 'normal'


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from Markdown content"""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            frontmatter[key] = value
    return frontmatter
