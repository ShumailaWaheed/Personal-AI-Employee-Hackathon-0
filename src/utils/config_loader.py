"""
Configuration Loader
Loads and manages configuration from environment variables and .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv


def load_config():
    """Load configuration from environment variables and .env file"""
    # Load environment variables from .env file
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(env_path)

    # Return configuration dictionary with defaults
    config = {
        'VAULT_PATH': os.getenv('VAULT_PATH', './AI_Employee_Vault'),
        'CHECK_INTERVAL': int(os.getenv('CHECK_INTERVAL', '60')),
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'DRY_RUN': os.getenv('DRY_RUN', 'false').lower() == 'true',
    }

    return config


def validate_config(config):
    """Validate the configuration settings"""
    errors = []

    # Validate vault path
    vault_path = Path(config['VAULT_PATH'])
    if not vault_path.exists():
        errors.append(f"Vault path does not exist: {vault_path}")

    # Validate check interval
    if config['CHECK_INTERVAL'] <= 0:
        errors.append("CHECK_INTERVAL must be greater than 0")

    # Validate log level
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    if config['LOG_LEVEL'] not in valid_log_levels:
        errors.append(f"LOG_LEVEL must be one of {valid_log_levels}")

    return len(errors) == 0, errors