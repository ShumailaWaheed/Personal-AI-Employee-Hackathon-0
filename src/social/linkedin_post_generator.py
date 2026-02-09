"""
LinkedIn Post Generator
Generates LinkedIn post content based on business goals and Company_Handbook.md
"""
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class LinkedInPostGenerator:
    """Generates LinkedIn post drafts based on business context"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.handbook_path = self.vault_path / 'Company_Handbook.md'

    def _load_handbook(self) -> str:
        if self.handbook_path.exists():
            return self.handbook_path.read_text(encoding='utf-8')
        return ""

    def generate_post(self, topic: str, style: str = "professional") -> dict:
        """Generate a LinkedIn post draft"""
        handbook = self._load_handbook()

        # Extract relevant company info for context
        company_context = self._extract_context(handbook, topic)

        post = {
            "topic": topic,
            "style": style,
            "content": self._create_post_content(topic, style, company_context),
            "hashtags": self._suggest_hashtags(topic),
            "generated_at": datetime.now().isoformat(),
            "status": "draft",
        }
        return post

    def _create_post_content(self, topic: str, style: str, context: str) -> str:
        """Create post content - in production this would use Claude"""
        # Template-based generation (Claude skill would enhance this)
        templates = {
            "professional": (
                f"Excited to share insights on {topic}.\n\n"
                f"Key takeaways:\n"
                f"- Innovation drives growth\n"
                f"- Collaboration creates value\n"
                f"- Continuous learning is essential\n\n"
                f"What are your thoughts on this topic?\n\n"
            ),
            "thought_leadership": (
                f"The landscape of {topic} is evolving rapidly.\n\n"
                f"Here are three trends I'm watching:\n"
                f"1. Increasing automation and AI integration\n"
                f"2. Shift towards sustainable practices\n"
                f"3. Growing importance of data-driven decisions\n\n"
                f"How is your organization adapting?\n\n"
            ),
            "engagement": (
                f"Quick question for my network:\n\n"
                f"How are you approaching {topic} in your work?\n\n"
                f"I'd love to hear different perspectives.\n\n"
            ),
        }
        return templates.get(style, templates["professional"])

    def _suggest_hashtags(self, topic: str) -> list[str]:
        """Suggest relevant hashtags"""
        base = ["#business", "#innovation", "#growth"]
        topic_tags = [f"#{word.lower()}" for word in topic.split()[:3] if len(word) > 3]
        return base + topic_tags

    def _extract_context(self, handbook: str, topic: str) -> str:
        """Extract relevant context from handbook for the topic"""
        if not handbook:
            return ""
        lines = handbook.split('\n')
        relevant = []
        for line in lines:
            if topic.lower() in line.lower():
                relevant.append(line.strip())
        return '\n'.join(relevant[:5])

    def create_post_action_file(self, post: dict, output_dir: Path) -> Path:
        """Create a Needs_Action file for a LinkedIn post"""
        ts = int(datetime.now().timestamp())
        filename = f"linkedin_post_{ts}.md"
        filepath = output_dir / filename

        content = f"""# LinkedIn Post Draft

## Post Content
{post['content']}

## Hashtags
{' '.join(post['hashtags'])}

## Details
- **Topic**: {post['topic']}
- **Style**: {post['style']}
- **Generated**: {post['generated_at']}
- **Status**: {post['status']}

## Action Required
Review and approve this LinkedIn post before publishing.
"""
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created LinkedIn post draft: {filepath.name}")
        return filepath
