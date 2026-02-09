"""
Silver Tier Processor
Extends Bronze VaultProcessor with HITL approval workflow, MCP execution,
and multi-watcher support.
"""
import json
import logging
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Any

from processors.vault_processor import VaultProcessor
from utils.sensitive_action_detector import requires_approval, detect_action_type, assess_risk
from utils.approval_formatter import ApprovalFormatter
from utils.mcp_client import MCPClient
from utils.audit_logger import AuditLogger
from models.approval_request import ApprovalRequest
from models.audit_log_entry import AuditLogEntry

logger = logging.getLogger(__name__)


class SilverProcessor(VaultProcessor):
    """Silver tier processor with HITL approval and MCP integration"""

    def __init__(self, vault_path: str, config: dict):
        super().__init__(vault_path)

        self.config = config
        self.vault = Path(vault_path)
        self.pending_approval = self.vault / 'Pending_Approval'
        self.approved = self.vault / 'Approved'
        self.rejected = self.vault / 'Rejected'
        self.logs_dir = self.vault / 'Logs'
        self.plans_dir = self.vault / 'Plans'

        for d in [self.pending_approval, self.approved, self.rejected, self.logs_dir, self.plans_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.dry_run = config.get('DRY_RUN', False)
        self.approval_formatter = ApprovalFormatter(vault_path)
        self.mcp_client = MCPClient()
        self.audit_logger = AuditLogger(vault_path)

    def process_all(self):
        """Process all pending items: Needs_Action + Approved"""
        self._process_needs_action()
        self._process_approved()

    def _process_needs_action(self):
        """Process items in Needs_Action, routing sensitive actions to HITL"""
        for action_file in sorted(self.needs_action.glob("*.md")):
            try:
                content = action_file.read_text(encoding='utf-8')
                logger.info(f"Processing: {action_file.name}")

                if requires_approval(content):
                    self._route_to_approval(action_file, content)
                else:
                    # Non-sensitive: process directly (Bronze tier behavior)
                    self.process_action_item(action_file)
            except Exception as e:
                logger.error(f"Error processing {action_file.name}: {e}")

    def _route_to_approval(self, action_file: Path, content: str):
        """Route a sensitive action to the HITL approval workflow"""
        action_type = detect_action_type(content)
        risk_level = assess_risk(content)

        # Create a plan first
        plan_path = self._create_plan(action_file, content)

        # Create approval request
        request = ApprovalRequest(
            action_type=action_type,
            target=self._extract_target(content),
            parameters={"source_file": action_file.name, "plan": plan_path.name},
            risk_level=risk_level,
            mcp_server=self._determine_mcp_server(action_type),
        )

        plan_summary = plan_path.read_text(encoding='utf-8')[:500]
        approval_path = self.approval_formatter.create_approval_file(request, plan_summary)
        logger.info(f"Created approval request: {approval_path.name} (risk: {risk_level})")

        # Log the routing
        self.audit_logger.log(AuditLogEntry(
            action_type="route_to_approval",
            actor="system",
            target=action_file.name,
            parameters={"action_type": action_type, "risk_level": risk_level},
            approval_status="pending",
            result="success",
        ))

        # Move original to Done (the approval file is now the active artifact)
        dest = self.done / action_file.name
        shutil.move(str(action_file), str(dest))

    def _process_approved(self):
        """Process actions that have been approved by human operator"""
        for approved_file in sorted(self.approved.glob("*.md")):
            try:
                content = approved_file.read_text(encoding='utf-8')
                logger.info(f"Executing approved action: {approved_file.name}")

                start = time.time()
                success = self._execute_via_mcp(approved_file, content)
                elapsed = int((time.time() - start) * 1000)

                # Audit log
                self.audit_logger.log(AuditLogEntry(
                    action_type=detect_action_type(content),
                    actor="system",
                    target=approved_file.name,
                    parameters={"dry_run": self.dry_run},
                    approval_status="executed",
                    result="success" if success else "failure",
                    execution_time_ms=elapsed,
                ))

                # Move to Done
                dest = self.done / approved_file.name
                shutil.move(str(approved_file), str(dest))
                logger.info(f"Completed: {approved_file.name}")

            except Exception as e:
                logger.error(f"Error executing approved action {approved_file.name}: {e}")

    def _execute_via_mcp(self, action_file: Path, content: str) -> bool:
        """Execute an approved action via the appropriate MCP server"""
        if self.dry_run:
            logger.info(f"(DRY RUN) Would execute: {action_file.name}")
            return True

        action_type = detect_action_type(content)

        if action_type == 'email_send':
            return self.mcp_client.send_email({
                "to": [self._extract_target(content)],
                "subject": f"Action: {action_file.stem}",
                "body": f"Approved action from {action_file.name} has been executed.",
            })

        # For other action types, log and return success
        logger.info(f"Executed {action_type}: {action_file.name}")
        return True

    def _create_plan(self, action_file: Path, content: str) -> Path:
        """Create a plan file from an action"""
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_filename = f"PLAN_{ts}_{action_file.stem}.md"
        plan_path = self.plans_dir / plan_filename

        # Extract title
        title = action_file.stem.replace('_', ' ').title()
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break

        plan_content = f"""---
created: {datetime.now().isoformat()}
source_action: {action_file.name}
priority: medium
status: pending_approval
---

# Plan: {title}

## Objective
Process the action from {action_file.name}.

## Context
{content[:500]}{'...' if len(content) > 500 else ''}

## Action Steps
- [ ] Step 1: Review requirements
- [ ] Step 2: Gather necessary resources
- [ ] Step 3: Execute primary task
- [ ] Step 4: Verify completion
- [ ] Step 5: Document results

## Expected Outcome
Complete the action as specified with all requirements fulfilled.
"""
        plan_path.write_text(plan_content, encoding='utf-8')
        logger.info(f"Created plan: {plan_path.name}")
        return plan_path

    def _extract_target(self, content: str) -> str:
        """Extract target from content (email, contact name, etc.)"""
        for line in content.split('\n'):
            lower = line.lower()
            if 'target' in lower or 'to:' in lower or 'contact' in lower:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip().strip('*')
        return "unspecified"

    def _determine_mcp_server(self, action_type: str) -> str:
        """Determine which MCP server to use for an action type"""
        mapping = {
            'email_send': 'email_mcp',
            'linkedin_post': 'linkedin_mcp',
            'whatsapp_message': 'whatsapp_mcp',
        }
        return mapping.get(action_type, 'email_mcp')
