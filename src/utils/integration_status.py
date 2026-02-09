"""
Integration Status Tracker
Tracks health and status of all MCP server integrations
"""
import json
import logging
from pathlib import Path
from datetime import datetime

from models.mcp_server_status import MCPServerStatus

logger = logging.getLogger(__name__)

# Default server capabilities
DEFAULT_CAPABILITIES = {
    'email': ['send_email', 'validate_recipients', 'get_account_info'],
    'odoo': ['create_expense', 'create_invoice', 'get_financial_summary'],
    'twitter': ['post_tweet', 'get_engagement_metrics'],
    'linkedin': ['create_post', 'get_post_metrics'],
    'whatsapp': ['send_message', 'get_message_status'],
}


class IntegrationStatusTracker:
    """Tracks MCP server health in integration_status.json"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.status_path = self.vault_path / 'Business' / 'integration_status.json'
        self.status_path.parent.mkdir(parents=True, exist_ok=True)
        self._servers: dict[str, MCPServerStatus] = {}
        self.load_status()

    def load_status(self):
        """Load integration status from JSON file"""
        if not self.status_path.exists():
            self._init_defaults()
            return

        try:
            data = json.loads(self.status_path.read_text(encoding='utf-8'))
            servers = data.get('servers', {})
            for name, server_data in servers.items():
                self._servers[name] = MCPServerStatus.from_dict(name, server_data)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load integration status: {e}")
            self._init_defaults()

    def _init_defaults(self):
        """Initialize default server statuses"""
        for name, caps in DEFAULT_CAPABILITIES.items():
            self._servers[name] = MCPServerStatus(
                server_name=name,
                capabilities=caps,
            )

    def save_status(self):
        """Save integration status to JSON file"""
        data = {
            "servers": {name: s.to_dict() for name, s in self._servers.items()},
            "last_updated": datetime.now().isoformat(),
        }
        self.status_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def update_status(self, server_name: str, success: bool):
        """Update a server's status after an operation"""
        if server_name not in self._servers:
            self._servers[server_name] = MCPServerStatus(server_name=server_name)

        server = self._servers[server_name]
        if success:
            server.record_success()
        else:
            server.record_failure()

        self.save_status()

    def get_health(self, server_name: str) -> str:
        """Get a server's health status"""
        if server_name in self._servers:
            return self._servers[server_name].status
        return "unknown"

    def get_all_statuses(self) -> dict[str, MCPServerStatus]:
        return dict(self._servers)
