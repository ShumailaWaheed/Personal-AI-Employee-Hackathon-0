"""
Gold Tier Processor
Extends SilverProcessor with autonomous processing, priority sorting,
domain classification, auto-approval for low-risk actions, retry queue
processing, and scheduled task execution.
"""
import logging
import shutil
import time
from pathlib import Path
from datetime import datetime

from processors.silver_processor import SilverProcessor
from utils.priority_classifier import classify_priority, parse_frontmatter
from utils.domain_classifier import classify_domain
from utils.sensitive_action_detector import requires_approval, detect_action_type, assess_risk
from utils.approval_formatter import ApprovalFormatter
from utils.retry_manager import RetryManager
from utils.scheduler import Scheduler
from utils.report_generator import ReportGenerator
from models.approval_request import ApprovalRequest
from models.audit_log_entry import AuditLogEntry
from models.retry_queue_entry import RetryQueueEntry

logger = logging.getLogger(__name__)


class GoldProcessor(SilverProcessor):
    """Gold tier processor with autonomous processing and business intelligence"""

    PRIORITY_ORDER = {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}

    def __init__(self, vault_path: str, config: dict):
        super().__init__(vault_path, config)

        self.gold_enabled = config.get('GOLD_TIER_ENABLED', False)
        self.auto_approve_low_risk = config.get('AUTO_APPROVE_LOW_RISK', False)

        # Gold-tier directories
        self.business_dir = self.vault / 'Business'
        self.accounting_dir = self.business_dir / 'Accounting'
        self.social_dir = self.business_dir / 'Social'
        self.briefings_dir = self.vault / 'Briefings'

        for d in [self.business_dir, self.accounting_dir, self.social_dir, self.briefings_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Retry manager
        self.retry_manager = RetryManager(vault_path)

        # Scheduler for weekly reports
        self.scheduler = Scheduler(vault_path)
        self.scheduler.configure('weekly_audit', config.get('AUDIT_SCHEDULE', 'monday:09:00'))
        self.scheduler.configure('weekly_briefing', config.get('BRIEFING_SCHEDULE', 'monday:10:00'))

        # Report generator
        self.report_generator = ReportGenerator(vault_path)

    def process_all(self):
        """Process all pending items with Gold-tier enhancements"""
        if not self.gold_enabled:
            # Fall back to Silver behavior
            super().process_all()
            return

        self._process_needs_action_gold()
        self._process_approved()
        self._process_retry_queue()
        self._process_scheduled_tasks()

    def _process_needs_action_gold(self):
        """Process Needs_Action items with priority sorting and domain classification"""
        action_files = sorted(self.needs_action.glob("*.md"))
        if not action_files:
            return

        # Parse and classify all items
        classified = []
        for action_file in action_files:
            try:
                content = action_file.read_text(encoding='utf-8')
                frontmatter = parse_frontmatter(content)
                priority = classify_priority(content, frontmatter)
                domain = classify_domain(content, frontmatter)
                classified.append((action_file, content, frontmatter, priority, domain))
            except Exception as e:
                logger.error(f"Error classifying {action_file.name}: {e}")

        # Sort by priority (urgent first)
        classified.sort(key=lambda x: self.PRIORITY_ORDER.get(x[3], 2))

        # Process in priority order
        for action_file, content, frontmatter, priority, domain in classified:
            try:
                logger.info(f"Processing: {action_file.name} [priority={priority}, domain={domain}]")
                self._process_single_action(action_file, content, frontmatter, priority, domain)
            except Exception as e:
                logger.error(f"Error processing {action_file.name}: {e}")

    def _extract_draft_reply(self, content: str) -> str:
        """Extract draft reply text from action file content"""
        lines = content.split('\n')
        in_section = False
        reply_lines = []
        for line in lines:
            if line.strip().startswith('## Draft Reply'):
                in_section = True
                continue
            if in_section:
                if line.strip().startswith('## '):
                    break
                reply_lines.append(line)
        return '\n'.join(reply_lines).strip()

    def _extract_message_content(self, content: str) -> str:
        """Extract the original message content from action file"""
        lines = content.split('\n')
        in_section = False
        msg_lines = []
        for line in lines:
            if line.strip().startswith('## Message Content'):
                in_section = True
                continue
            if in_section:
                if line.strip().startswith('## '):
                    break
                # Strip blockquote marker
                text = line.lstrip('> ').strip() if line.startswith('>') else line
                msg_lines.append(text)
        return '\n'.join(msg_lines).strip()

    def _process_single_action(self, action_file: Path, content: str, frontmatter: dict,
                                priority: str, domain: str):
        """Process a single action item with Gold-tier logic"""
        if requires_approval(content):
            action_type = detect_action_type(content)
            risk_level = assess_risk(content)

            # Extract draft reply for whatsapp keyword-triggered messages
            draft_reply = ""
            if action_type == 'whatsapp_message':
                draft_reply = self._extract_draft_reply(content)

            # Auto-approval check
            if self._can_auto_approve(risk_level, domain):
                self._auto_approve_action(action_file, content, action_type, risk_level, domain)
            else:
                self._route_to_approval_gold(
                    action_file, content, action_type, risk_level, domain,
                    draft_reply=draft_reply,
                )
        else:
            # Non-sensitive: process directly (Bronze behavior)
            self.process_action_item(action_file)

    def _can_auto_approve(self, risk_level: str, domain: str) -> bool:
        """Determine if an action can be auto-approved"""
        if not self.auto_approve_low_risk:
            return False
        if risk_level != 'low':
            return False
        if domain == 'cross-domain':
            return False
        return True

    def _auto_approve_action(self, action_file: Path, content: str,
                              action_type: str, risk_level: str, domain: str):
        """Auto-approve and execute a low-risk action"""
        logger.info(f"Auto-approving low-risk action: {action_file.name}")

        # Log the auto-approval
        self.audit_logger.log(AuditLogEntry(
            action_type=action_type,
            actor="system",
            target=action_file.name,
            parameters={"risk_level": risk_level, "auto_approved": True},
            approval_status="auto_approved",
            result="success",
            domain=domain,
        ))

        # Execute via MCP (in dry-run it'll be logged only)
        start = time.time()
        success = self._execute_via_mcp(action_file, content)
        elapsed = int((time.time() - start) * 1000)

        self.audit_logger.log(AuditLogEntry(
            action_type=action_type,
            actor="system",
            target=action_file.name,
            parameters={"dry_run": self.dry_run, "auto_approved": True},
            approval_status="executed",
            result="success" if success else "failure",
            execution_time_ms=elapsed,
            domain=domain,
        ))

        # Move to Done
        dest = self.done / action_file.name
        shutil.move(str(action_file), str(dest))

    def _route_to_approval_gold(self, action_file: Path, content: str,
                                 action_type: str, risk_level: str, domain: str,
                                 draft_reply: str = ""):
        """Route to HITL approval with Gold-tier metadata"""
        plan_path = self._create_plan(action_file, content)

        request = ApprovalRequest(
            action_type=action_type,
            target=self._extract_target(content),
            parameters={"source_file": action_file.name, "plan": plan_path.name},
            risk_level=risk_level,
            mcp_server=self._determine_mcp_server(action_type),
            domain=domain,
            approval_source="pending",
        )

        plan_summary = plan_path.read_text(encoding='utf-8')[:500]
        approval_path = self.approval_formatter.create_approval_file(
            request, plan_summary, draft_reply=draft_reply,
        )
        logger.info(f"Created approval request: {approval_path.name} "
                     f"(risk: {risk_level}, domain: {domain})")

        self.audit_logger.log(AuditLogEntry(
            action_type="route_to_approval",
            actor="system",
            target=action_file.name,
            parameters={"action_type": action_type, "risk_level": risk_level, "domain": domain},
            approval_status="pending",
            result="success",
            domain=domain,
        ))

        dest = self.done / action_file.name
        shutil.move(str(action_file), str(dest))

    def _process_retry_queue(self):
        """Process items in the retry queue that are ready for retry"""
        ready = self.retry_manager.get_ready_entries()
        for entry in ready:
            try:
                logger.info(f"Retrying: {entry.id} (attempt {entry.retry_count + 1}/{entry.max_retries})")
                entry.status = 'retrying'
                self.retry_manager.save_queue()

                # Attempt execution via MCP
                response = self.mcp_client._call_server(
                    entry.mcp_server, entry.operation, entry.parameters
                )

                if 'error' not in response:
                    self.retry_manager.remove_entry(entry.id)
                    logger.info(f"Retry successful: {entry.id}")
                else:
                    error_msg = response['error'].get('message', 'Unknown error')
                    self.retry_manager.update_entry(entry.id, 'queued', error_msg)

                    if entry.retry_count + 1 >= entry.max_retries:
                        self._notify_permanent_failure(entry)

            except Exception as e:
                logger.error(f"Retry failed for {entry.id}: {e}")
                self.retry_manager.update_entry(entry.id, 'queued', str(e))

    def _notify_permanent_failure(self, entry: RetryQueueEntry):
        """Create a notification file for permanent failure"""
        notification = self.needs_action / f"ALERT_retry_failed_{entry.id}.md"
        notification.write_text(
            f"---\npriority: urgent\ndomain: business\n---\n"
            f"# ALERT: Permanent Failure\n\n"
            f"**Operation**: {entry.operation}\n"
            f"**MCP Server**: {entry.mcp_server}\n"
            f"**Error**: {entry.error}\n"
            f"**Retries Exhausted**: {entry.retry_count}/{entry.max_retries}\n\n"
            f"This operation has failed permanently after {entry.max_retries} retries. "
            f"Please investigate and retry manually.\n",
            encoding='utf-8',
        )
        logger.warning(f"Permanent failure notification created for {entry.id}")

    def _process_scheduled_tasks(self):
        """Check and execute scheduled tasks (weekly audit, briefing)"""
        try:
            if self.scheduler.is_due('weekly_audit'):
                logger.info("Generating weekly audit report...")
                audit_path = self.report_generator.generate_audit_report()
                self.scheduler.mark_completed('weekly_audit')

                self.audit_logger.log(AuditLogEntry(
                    action_type="generate_audit_report",
                    actor="system",
                    target=audit_path.name,
                    approval_status="direct",
                    result="success",
                    domain="business",
                ))

            if self.scheduler.is_due('weekly_briefing'):
                logger.info("Generating executive briefing...")
                # Find the most recent audit to base briefing on
                briefings_dir = self.vault / 'Briefings'
                audits = sorted(briefings_dir.glob("audit_*.md"))
                if audits:
                    briefing_path = self.report_generator.generate_executive_briefing(audits[-1])
                    self.scheduler.mark_completed('weekly_briefing')

                    self.audit_logger.log(AuditLogEntry(
                        action_type="generate_executive_briefing",
                        actor="system",
                        target=briefing_path.name,
                        approval_status="direct",
                        result="success",
                        domain="business",
                    ))
        except Exception as e:
            logger.error(f"Error processing scheduled tasks: {e}")

    def _execute_via_mcp(self, action_file: Path, content: str) -> bool:
        """Execute an approved action via the appropriate MCP server (Gold-tier override)"""
        if self.dry_run:
            logger.info(f"(DRY RUN) Would execute: {action_file.name}")
            return True

        action_type = detect_action_type(content)

        if action_type == 'linkedin_post':
            text = self._extract_post_text(content)
            result = self.mcp_client.create_linkedin_post({'text': text})
            success = isinstance(result, dict) and result.get('success', False)
            if success:
                logger.info(f"LinkedIn post published: {result.get('post_id', 'unknown')}")
            else:
                logger.error(f"LinkedIn post failed: {result}")
            return success

        if action_type == 'facebook_post':
            text = self._extract_post_text(content)
            result = self.mcp_client.create_facebook_post({'message': text})
            success = isinstance(result, dict) and result.get('success', False)
            if success:
                logger.info(f"Facebook post published: {result.get('post_id', 'unknown')}")
            else:
                logger.error(f"Facebook post failed: {result}")
            return success

        if action_type == 'twitter_post':
            text = self._extract_post_text(content)
            result = self.mcp_client.create_tweet({'text': text})
            success = isinstance(result, dict) and result.get('success', False)
            if success:
                logger.info(f"Tweet published: {result.get('tweet_id', 'unknown')}")
            else:
                logger.error(f"Tweet failed: {result}")
            return success

        if action_type == 'instagram_post':
            text = self._extract_post_text(content)
            result = self.mcp_client.create_instagram_post({
                'caption': text,
                'image_url': self._extract_image_url(content),
            })
            success = isinstance(result, dict) and result.get('success', False)
            if success:
                logger.info(f"Instagram post published: {result.get('post_id', 'unknown')}")
            else:
                logger.error(f"Instagram post failed: {result}")
            return success

        if action_type == 'whatsapp_message':
            # Prefer draft reply from approval file; fall back to generic extraction
            draft = self._extract_draft_reply(content)
            message = draft if draft else self._extract_post_text(content)
            result = self.mcp_client.send_whatsapp({
                'to': self._extract_target(content),
                'message': message,
            })
            return isinstance(result, dict) and result.get('success', False)

        if action_type == 'financial_action':
            result = self.mcp_client.create_expense({
                'description': self._extract_post_text(content),
                'amount': 0,
                'currency': 'USD',
            })
            return isinstance(result, dict) and result.get('success', False)

        # Fall back to Silver behavior for email and other types
        return super()._execute_via_mcp(action_file, content)

    def _extract_post_text(self, content: str) -> str:
        """Extract the main post/message text from action content"""
        lines = content.split('\n')
        text_lines = []
        in_quote = False
        for line in lines:
            # Once inside a quote, capture everything until closing quote
            if in_quote:
                if '"' in line:
                    end = line.index('"')
                    text_lines.append(line[:end])
                    return '\n'.join(text_lines)
                text_lines.append(line)
                continue
            # Skip frontmatter
            if line.strip() == '---':
                continue
            # Skip headers and metadata
            if line.startswith('#') or line.startswith('**') or line.startswith('- '):
                continue
            # Capture quoted text (between quotation marks)
            if '"' in line:
                start = line.index('"') + 1
                if line.count('"') >= 2:
                    end = line.rindex('"')
                    return line[start:end]
                in_quote = True
                text_lines.append(line[start:])
                continue
        # If no quoted text found, return content after headers
        if text_lines:
            return '\n'.join(text_lines)
        # Last resort: return everything after frontmatter
        body_lines = []
        past_frontmatter = False
        frontmatter_count = 0
        for line in lines:
            if line.strip() == '---':
                frontmatter_count += 1
                if frontmatter_count == 2:
                    past_frontmatter = True
                continue
            if past_frontmatter and not line.startswith('#'):
                body_lines.append(line)
        return '\n'.join(body_lines).strip()

    def _extract_image_url(self, content: str) -> str:
        """Extract image URL from action content for Instagram posts"""
        for line in content.split('\n'):
            line_stripped = line.strip()
            if line_stripped.startswith('image_url:'):
                return line_stripped.split(':', 1)[1].strip()
            if line_stripped.startswith('!['):
                # Markdown image: ![alt](url)
                start = line_stripped.index('(') + 1
                end = line_stripped.index(')')
                return line_stripped[start:end]
        return ''

    def _determine_mcp_server(self, action_type: str) -> str:
        """Determine MCP server — extends Silver mapping with Gold servers"""
        mapping = {
            'email_send': 'email_mcp',
            'linkedin_post': 'linkedin_mcp',
            'whatsapp_message': 'whatsapp_mcp',
            'twitter_post': 'twitter_mcp',
            'instagram_post': 'instagram_mcp',
            'financial_action': 'odoo_mcp',
        }
        return mapping.get(action_type, 'email_mcp')
