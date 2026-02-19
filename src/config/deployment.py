"""
Deployment mode detection and configuration for cloud/local split.
Cloud (GCP e2-micro): lightweight watchers + API-only MCP servers
Local (Windows): Playwright-based services (WhatsApp, Twitter, Instagram)
"""
import os
from pathlib import Path


def is_cloud() -> bool:
    """Check if running in cloud deployment mode."""
    return os.getenv('DEPLOYMENT_MODE', 'local').lower() == 'cloud'


def is_local() -> bool:
    """Check if running in local deployment mode."""
    return not is_cloud()


def get_vault_path() -> Path:
    """Returns vault path for current deployment mode."""
    return Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))


def get_enabled_watchers() -> list[str]:
    """Returns watcher names enabled for this deployment mode."""
    if is_cloud():
        return ['file_system', 'gmail', 'linkedin']
    return ['file_system', 'gmail', 'linkedin', 'whatsapp']


def get_enabled_mcp_servers() -> list[str]:
    """Returns MCP server names available in this deployment mode.
    Browser-based servers (whatsapp, twitter, instagram) not available on cloud.
    """
    if is_cloud():
        return ['email', 'linkedin', 'facebook', 'odoo']
    return ['email', 'linkedin', 'facebook', 'odoo', 'whatsapp', 'twitter', 'instagram']
