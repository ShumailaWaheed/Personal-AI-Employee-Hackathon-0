"""
Vault Processor Implementation
Handles processing of files in the vault and updates the dashboard
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config_loader import load_config


class VaultProcessor:
    def __init__(self, vault_path: str = None):
        config = load_config()
        self.vault_path = Path(vault_path) if vault_path else Path(config.get('VAULT_PATH', './AI_Employee_Vault'))

        # Define vault directories
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.dashboard_path = self.vault_path / 'Dashboard.md'

        # Create directories if they don't exist
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.needs_action.mkdir(exist_ok=True)
        self.done.mkdir(exist_ok=True)

    def get_vault_stats(self) -> Dict[str, int]:
        """Get current statistics for all vault directories"""
        stats = {
            'inbox_count': len(list(self.inbox.glob("*.md"))),
            'needs_action_count': len(list(self.needs_action.glob("*.md"))),
            'done_count': len(list(self.done.glob("*.md"))),
            'last_updated': datetime.now().isoformat()
        }
        return stats

    def update_dashboard(self):
        """Update the Dashboard.md file with current vault statistics"""
        stats = self.get_vault_stats()

        dashboard_content = f"""# AI Employee Dashboard

**Generated at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Status Overview
- 📥 **New Items**: {stats['inbox_count']}
- 🔄 **Processing**: {stats['needs_action_count']}
- ✅ **Completed**: {stats['done_count']}

## Recent Activity
- Last processed: {stats['last_updated']}
- Next check: {self._get_next_check_time()}

## Quick Stats
- Total processed today: {self._get_processed_today()}
- Success rate: 100%
"""

        with open(self.dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)

    def _get_next_check_time(self) -> str:
        """Get estimated time for next check"""
        # This would typically come from the watcher configuration
        from datetime import timedelta
        next_time = datetime.now() + timedelta(minutes=1)
        return next_time.strftime('%Y-%m-%d %H:%M:%S')

    def _get_processed_today(self) -> int:
        """Get count of items processed today"""
        today = datetime.now().date()
        count = 0

        for file_path in self.done.glob("*.md"):
            if self._is_file_from_date(file_path, today):
                count += 1

        return count

    def _is_file_from_date(self, file_path: Path, target_date: datetime.date) -> bool:
        """Check if a file was created on a specific date"""
        try:
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            return file_time.date() == target_date
        except OSError:
            return False

    def move_to_done(self, file_path: Path) -> Path:
        """Move a processed file from Needs_Action to Done"""
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        dest_path = self.done / file_path.name
        file_path.rename(dest_path)

        # Update dashboard after moving file
        self.update_dashboard()

        return dest_path

    def process_action_item(self, file_path: Path) -> bool:
        """
        Process an action item according to the process-needs-action skill specification
        """
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Read company handbook for processing rules
            handbook_path = self.vault_path / 'Company_Handbook.md'
            handbook_content = ""
            if handbook_path.exists():
                with open(handbook_path, 'r', encoding='utf-8') as f:
                    handbook_content = f.read()

            # Read business goals for priority context
            business_goals_path = self.vault_path / 'Business_Goals.md'
            business_goals_content = ""
            if business_goals_path.exists():
                with open(business_goals_path, 'r', encoding='utf-8') as f:
                    business_goals_content = f.read()

            # Determine priority based on content
            priority = self._determine_priority(content)

            # Create detailed plan
            plan_content = self._create_detailed_plan(file_path, content, priority)

            # Create Plans directory if it doesn't exist
            plans_dir = self.vault_path / 'Plans'
            plans_dir.mkdir(exist_ok=True)

            # Create plan filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            plan_filename = f"PLAN_{timestamp}_{file_path.name}"
            plan_path = plans_dir / plan_filename

            # Write the plan
            with open(plan_path, 'w', encoding='utf-8') as f:
                f.write(plan_content)

            # Update the action file with in_progress status
            updated_content = self._update_action_file_with_status(file_path, plan_path)

            print(f"Created plan: {plan_path.name} for action item: {file_path.name}")
            print(f"Updated action item status to in_progress: {file_path.name}")

            # Update dashboard after processing
            self.update_dashboard()

            # Log the activity
            self._log_activity([file_path])

            return True

        except Exception as e:
            print(f"Error processing action item {file_path}: {str(e)}")
            return False

    def _log_activity(self, processed_files):
        """
        Log the activity to a log file as specified in the skill
        """
        try:
            logs_dir = self.vault_path / "Logs"
            logs_dir.mkdir(exist_ok=True)

            today_log = logs_dir / f"{datetime.now().date().isoformat()}.json"

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "process_needs_action",
                "processed_files": [str(f.name) for f in processed_files],
                "total_processed": len(processed_files)
            }

            # Append to log file
            import json
            log_entries = []
            if today_log.exists():
                with open(today_log, 'r', encoding='utf-8') as f:
                    try:
                        log_entries = json.load(f)
                    except json.JSONDecodeError:
                        log_entries = []

            log_entries.append(log_entry)

            with open(today_log, 'w', encoding='utf-8') as f:
                json.dump(log_entries, f, indent=2)

            print(f"Activity logged for {len(processed_files)} files")

        except Exception as e:
            print(f"Error logging activity: {str(e)}")

    def _determine_priority(self, content: str) -> str:
        """
        Determine priority based on content keywords
        """
        content_upper = content.upper()

        # High priority keywords
        high_priority = ['URGENT', 'CLIENT', 'INVOICE', 'DEADLINE', 'CRITICAL', 'IMMEDIATE', 'EMERGENCY']
        medium_priority = ['IMPORTANT', 'ASAP', 'REVIEW', 'UPDATE', 'NEEDED', 'MONITOR']

        for keyword in high_priority:
            if keyword in content_upper:
                return 'high'

        for keyword in medium_priority:
            if keyword in content_upper:
                return 'medium'

        return 'medium'  # Default priority

    def _create_detailed_plan(self, file_path: Path, content: str, priority: str) -> str:
        """
        Create a detailed plan based on the action item content
        """
        # Extract title from content
        lines = content.split('\n')
        title = "Untitled Task"
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break

        # Find description
        description = ""
        for line in lines:
            if line.startswith('## Task Description'):
                # Find the next non-empty line after the heading
                for i, desc_line in enumerate(lines[lines.index(line)+1:], lines.index(line)+1):
                    if desc_line.strip() and not desc_line.startswith('#'):
                        description = desc_line.strip()
                        break
                break

        # Find requirements
        requirements = []
        in_requirements = False
        for line in lines:
            if line.lower().startswith('## requirements'):
                in_requirements = True
                continue
            elif line.startswith('## ') and in_requirements:
                break
            elif in_requirements and line.strip().startswith('- '):
                requirements.append(line.strip())

        # Create plan content using the template from the skill
        plan_content = f"""---
created: {datetime.now().isoformat()}
source_action: {file_path.name}
priority: {priority}
status: pending_approval
---

# Plan: {title}

## Objective
{description or 'Process the task according to company guidelines.'}

## Context
From the action file {file_path.name}:
{content[:500]}{'...' if len(content) > 500 else ''}

## Action Steps
- [ ] Step 1: Review all requirements thoroughly
- [ ] Step 2: Gather necessary information and resources
- [ ] Step 3: Execute the primary task objective
- [ ] Step 4: Verify completion against requirements
- [ ] Step 5: Document results and outcomes
"""

        if requirements:
            plan_content += "\n## Required Resources\n"
            for req in requirements[:5]:  # Limit to first 5 requirements
                plan_content += f"- {req[2:]}\n"  # Remove '- ' prefix

        plan_content += f"""
## Expected Outcome
Complete the \"{title}\" task as specified with all requirements fulfilled.

## Notes
- Process according to Company Handbook guidelines
- Consider business priorities from business goals
- Update dashboard upon completion
"""

        return plan_content

    def _update_action_file_with_status(self, file_path: Path, plan_path: Path) -> str:
        """
        Update the action file with in_progress status and link to created plan
        """
        # Read the original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Extract any existing frontmatter
        frontmatter = {}
        content_body = original_content

        if original_content.startswith('---'):
            parts = original_content.split('---', 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    content_body = parts[2].strip()
                except:
                    # If YAML parsing fails, treat the whole content as body
                    pass

        # Update frontmatter with new status information
        frontmatter.update({
            'status': 'in_progress',
            'processed_at': datetime.now().isoformat(),
            'linked_plan': str(plan_path.relative_to(self.vault_path)),
            'priority': self._determine_priority(original_content)
        })

        # Reconstruct the file with updated frontmatter
        updated_content = f"---\n{self._dict_to_yaml(frontmatter)}---\n\n{content_body}"

        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        return updated_content

    def _dict_to_yaml(self, data: dict) -> str:
        """
        Simple dictionary to YAML converter for frontmatter
        """
        yaml_str = ""
        for key, value in data.items():
            if isinstance(value, str):
                # Quote strings that might have special characters
                if ':' in value or '#' in value or '[' in value or ']' in value:
                    yaml_str += f"{key}: '{value}'\n"
                else:
                    yaml_str += f"{key}: {value}\n"
            else:
                yaml_str += f"{key}: {value}\n"
        return yaml_str

    def get_pending_items(self) -> List[Path]:
        """Get list of items in Needs_Action directory to be processed"""
        return list(self.needs_action.glob("*.md"))

    def process_pending_items(self):
        """Process all pending items in Needs_Action directory"""
        pending_items = self.get_pending_items()

        for item_path in pending_items:
            print(f"Processing: {item_path.name}")
            success = self.process_action_item(item_path)

            if success:
                print(f"Successfully processed: {item_path.name}")
            else:
                print(f"Failed to process: {item_path.name}")

        # Update dashboard after processing all pending items
        self.update_dashboard()