"""
Logger Utility
Sets up centralized logging for the AI employee system
"""
import logging


def setup_logger(log_level: str = 'INFO'):
    """Set up centralized logging configuration"""
    # Convert string log level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Output to console
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance"""
    return logging.getLogger(name)