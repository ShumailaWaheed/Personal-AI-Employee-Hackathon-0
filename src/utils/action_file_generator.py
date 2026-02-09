"""
Action File Generator
Creates action files from watcher inputs following the vault structure
"""
from pathlib import Path
from datetime import datetime

from models.watcher_input import WatcherInput


class ActionFileGenerator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

    def generate(self, watcher_input: WatcherInput) -> Path:
        """Create an action file from a WatcherInput"""
        ts = int(datetime.now().timestamp())
        safe_source = "".join(c if c.isalnum() or c in '-_' else '_' for c in watcher_input.source_id)
        filename = f"{watcher_input.source_type}_{safe_source}_{ts}.md"
        filepath = self.needs_action / filename

        content = f"""# Action: {watcher_input.source_type.capitalize()} Input

## Source Details
- **Source**: {watcher_input.source_type}
- **Source ID**: {watcher_input.source_id}
- **Received**: {watcher_input.timestamp.isoformat()}
- **Action Required**: {watcher_input.action_required}

## Content
{watcher_input.content}

## Metadata
"""
        for key, value in watcher_input.metadata.items():
            content += f"- **{key}**: {value}\n"

        filepath.write_text(content, encoding='utf-8')
        return filepath
