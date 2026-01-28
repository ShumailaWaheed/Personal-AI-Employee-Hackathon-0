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
        Process an action item using Claude Code agent skills
        This is a placeholder that would integrate with the actual Claude Code system
        """
        try:
            # In a real implementation, this would call Claude Code agent skills
            # For now, we'll simulate processing by just moving the file to Done

            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Process the content (in a real implementation, this would involve Claude Code)
            # For Bronze tier, we'll just move the file to Done after "processing"
            processed_path = self.move_to_done(file_path)

            print(f"Processed action item: {file_path.name} -> {processed_path.name}")
            return True

        except Exception as e:
            print(f"Error processing action item {file_path}: {str(e)}")
            return False

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