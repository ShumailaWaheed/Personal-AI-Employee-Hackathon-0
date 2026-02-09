"""
Configuration Management for Gold Tier AI Employee
Extends Bronze/Silver tier config with Gold tier settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict:
    """Load configuration from environment variables and .env file"""
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(env_path)

    return {
        # Vault
        'VAULT_PATH': os.getenv('VAULT_PATH', './AI_Employee_Vault'),
        'CHECK_INTERVAL': int(os.getenv('CHECK_INTERVAL', '60')),
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'DRY_RUN': os.getenv('DRY_RUN', 'false').lower() == 'true',
        'PROCESSING_INTERVAL': int(os.getenv('PROCESSING_INTERVAL', '30')),

        # Email MCP
        'EMAIL_SMTP_HOST': os.getenv('EMAIL_SMTP_HOST', 'smtp.gmail.com'),
        'EMAIL_SMTP_PORT': int(os.getenv('EMAIL_SMTP_PORT', '587')),
        'EMAIL_SMTP_USERNAME': os.getenv('EMAIL_SMTP_USERNAME', ''),
        'EMAIL_SMTP_PASSWORD': os.getenv('EMAIL_SMTP_PASSWORD', ''),
        'EMAIL_FROM_ADDRESS': os.getenv('EMAIL_FROM_ADDRESS', ''),
        'EMAIL_RATE_LIMIT_PER_DAY': int(os.getenv('EMAIL_RATE_LIMIT_PER_DAY', '500')),

        # LinkedIn API
        'LINKEDIN_ACCESS_TOKEN': os.getenv('LINKEDIN_ACCESS_TOKEN', ''),
        'LINKEDIN_PERSONAL_ACCOUNT_ID': os.getenv('LINKEDIN_PERSONAL_ACCOUNT_ID', ''),

        # Audit
        'LOG_RETENTION_DAYS': int(os.getenv('LOG_RETENTION_DAYS', '90')),

        # Gold Tier - Autonomous Processing
        'GOLD_TIER_ENABLED': os.getenv('GOLD_TIER_ENABLED', 'false').lower() == 'true',
        'AUTO_APPROVE_LOW_RISK': os.getenv('AUTO_APPROVE_LOW_RISK', 'false').lower() == 'true',

        # Gold Tier - Scheduling
        'AUDIT_SCHEDULE': os.getenv('AUDIT_SCHEDULE', 'monday:09:00'),
        'BRIEFING_SCHEDULE': os.getenv('BRIEFING_SCHEDULE', 'monday:10:00'),

        # Odoo Accounting MCP
        'ODOO_URL': os.getenv('ODOO_URL', ''),
        'ODOO_DB': os.getenv('ODOO_DB', ''),
        'ODOO_USERNAME': os.getenv('ODOO_USERNAME', ''),
        'ODOO_API_KEY': os.getenv('ODOO_API_KEY', ''),

        # Twitter/X MCP
        'TWITTER_BEARER_TOKEN': os.getenv('TWITTER_BEARER_TOKEN', ''),
        'TWITTER_API_KEY': os.getenv('TWITTER_API_KEY', ''),
        'TWITTER_API_SECRET': os.getenv('TWITTER_API_SECRET', ''),

        # WhatsApp MCP
        'WHATSAPP_MODE': os.getenv('WHATSAPP_MODE', 'playwright'),
        'WHATSAPP_API_TOKEN': os.getenv('WHATSAPP_API_TOKEN', ''),
    }


def validate_config(config: dict) -> tuple[bool, list[str]]:
    """Validate configuration settings"""
    errors = []

    vault_path = Path(config['VAULT_PATH'])
    if not vault_path.exists():
        errors.append(f"Vault path does not exist: {vault_path}")

    if config['CHECK_INTERVAL'] <= 0:
        errors.append("CHECK_INTERVAL must be greater than 0")

    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    if config['LOG_LEVEL'] not in valid_log_levels:
        errors.append(f"LOG_LEVEL must be one of {valid_log_levels}")

    return len(errors) == 0, errors


# Sensitive action keywords for HITL detection
SENSITIVE_KEYWORDS = [
    'email', 'send', 'post', 'publish', 'share', 'message',
    'contact', 'reach out', 'reply', 'respond', 'payment',
    'transaction', 'buy', 'purchase', 'transfer', 'linkedin',
    # Gold tier additions
    'expense', 'invoice', 'accounting', 'bookkeeping', 'financial',
    'tweet', 'twitter', 'whatsapp',
]
