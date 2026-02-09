"""
LinkedIn Approval Flow
Integrates LinkedIn posting with the HITL approval workflow
"""
import logging
from pathlib import Path
from datetime import datetime

from social.linkedin_post_generator import LinkedInPostGenerator
from social.rate_limiter import RateLimiter
from social.performance_tracker import PerformanceTracker
from models.approval_request import ApprovalRequest
from utils.approval_formatter import ApprovalFormatter

logger = logging.getLogger(__name__)


class LinkedInApprovalFlow:
    """Orchestrates LinkedIn post generation through the approval pipeline"""

    def __init__(self, vault_path: str, max_posts_per_day: int = 3):
        self.vault_path = Path(vault_path)
        self.generator = LinkedInPostGenerator(vault_path)
        self.rate_limiter = RateLimiter(vault_path, max_posts_per_day)
        self.tracker = PerformanceTracker(vault_path)
        self.approval_formatter = ApprovalFormatter(vault_path)

    def create_post_for_approval(self, topic: str, style: str = "professional") -> Path | None:
        """Generate a LinkedIn post and route it for HITL approval"""
        if not self.rate_limiter.can_post():
            remaining = self.rate_limiter.remaining_posts()
            logger.warning(f"Rate limit reached. {remaining} posts remaining today.")
            return None

        post = self.generator.generate_post(topic, style)

        request = ApprovalRequest(
            action_type="linkedin_post",
            target="LinkedIn",
            parameters={
                "topic": topic,
                "style": style,
                "content_preview": post["content"][:200],
                "hashtags": " ".join(post["hashtags"]),
            },
            risk_level="medium",
            mcp_server="linkedin_mcp",
        )

        approval_path = self.approval_formatter.create_approval_file(
            request,
            plan_summary=post["content"],
        )

        logger.info(f"LinkedIn post routed for approval: {approval_path.name}")
        return approval_path

    def on_approved(self, post_content: str):
        """Called when a LinkedIn post is approved and executed"""
        self.rate_limiter.record_post()
        post_id = f"li_{int(datetime.now().timestamp())}"
        self.tracker.record_post(post_id, post_content)
        logger.info(f"LinkedIn post tracked: {post_id}")
