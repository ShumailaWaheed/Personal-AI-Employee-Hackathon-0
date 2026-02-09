"""
Logger Utility
Sets up centralized logging for the AI employee system
"""
import logging
from pathlib import Path


def setup_logger(log_level: str = 'INFO', log_dir: str = 'logs'):
    """Set up centralized logging configuration with file and console output"""
    level = getattr(logging, log_level.upper(), logging.INFO)

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path / 'ai-employee.log', encoding='utf-8'),
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance"""
    return logging.getLogger(name)