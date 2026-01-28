"""
Main Entry Point for Bronze-tier Personal AI Employee
"""
import sys
import signal
import logging
from pathlib import Path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from watchers.file_system_watcher import FileSystemWatcher
from processors.vault_processor import VaultProcessor
from utils.config_loader import load_config, validate_config
from utils.logger import setup_logger


def signal_handler(sig, frame):
    """Handle interrupt signals gracefully"""
    print("\nShutting down AI Employee...")
    sys.exit(0)


def main():
    """Main entry point for the AI Employee application"""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Load configuration
    config = load_config()

    # Validate configuration
    is_valid, errors = validate_config(config)
    if not is_valid:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    # Set up logging
    setup_logger(config['LOG_LEVEL'])

    # Initialize components
    watcher = FileSystemWatcher(config['VAULT_PATH'], config['CHECK_INTERVAL'])
    processor = VaultProcessor(config['VAULT_PATH'])

    print("Bronze-tier Personal AI Employee starting...")
    print(f"Vault path: {config['VAULT_PATH']}")
    print(f"Check interval: {config['CHECK_INTERVAL']} seconds")
    print(f"Log level: {config['LOG_LEVEL']}")
    print("Press Ctrl+C to stop")

    # Update dashboard initially
    processor.update_dashboard()

    try:
        # Start the file system watcher
        watcher.run()
    except KeyboardInterrupt:
        print("\nShutting down AI Employee...")
    except Exception as e:
        print(f"Error running AI Employee: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()