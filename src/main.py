"""
Main Entry Point for Gold Tier Personal AI Employee
Backward-compatible with Bronze and Silver tiers.
Gold tier adds: autonomous processing, priority/domain classification,
auto-approval, retry queue, scheduled reports.
"""
import sys
import signal
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from watchers.file_system_watcher import FileSystemWatcher
from processors.vault_processor import VaultProcessor
from processors.silver_processor import SilverProcessor
from processors.gold_processor import GoldProcessor
from utils.config_loader import load_config, validate_config
from utils.logger import setup_logger
from utils.dashboard_updater import DashboardUpdater


def signal_handler(sig, frame):
    """Handle interrupt signals gracefully"""
    print("\nShutting down AI Employee...")
    sys.exit(0)


def main():
    """Main entry point for the AI Employee application"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    config = load_config()

    is_valid, errors = validate_config(config)
    if not is_valid:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    setup_logger(config['LOG_LEVEL'])

    # Initialize processor based on tier
    gold_enabled = config.get('GOLD_TIER_ENABLED', False)
    if gold_enabled:
        processor = GoldProcessor(config['VAULT_PATH'], config)
        tier_name = "Gold"
    else:
        processor = SilverProcessor(config['VAULT_PATH'], config)
        tier_name = "Silver"

    # Initialize filesystem watcher (Bronze tier baseline)
    watcher = FileSystemWatcher(config['VAULT_PATH'], config['CHECK_INTERVAL'])

    # Dashboard updater
    dashboard = DashboardUpdater(config['VAULT_PATH'])

    print(f"{tier_name} Tier Personal AI Employee starting...")
    print(f"Vault path: {config['VAULT_PATH']}")
    print(f"Check interval: {config['CHECK_INTERVAL']} seconds")
    print(f"Processing interval: {config.get('PROCESSING_INTERVAL', 30)} seconds")
    print(f"Dry run: {config['DRY_RUN']}")
    if gold_enabled:
        print(f"Auto-approve low-risk: {config.get('AUTO_APPROVE_LOW_RISK', False)}")
    print("Press Ctrl+C to stop")

    # Initial dashboard update
    dashboard.update(dry_run=config['DRY_RUN'],
                     processing_interval=config.get('PROCESSING_INTERVAL', 30))

    try:
        # Process any pending items
        processor.process_all()

        # Update dashboard after initial processing
        dashboard.update(dry_run=config['DRY_RUN'],
                         processing_interval=config.get('PROCESSING_INTERVAL', 30))

        # Start the filesystem watcher (main loop)
        watcher.run()
    except KeyboardInterrupt:
        print("\nShutting down AI Employee...")
    except Exception as e:
        print(f"Error running AI Employee: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
