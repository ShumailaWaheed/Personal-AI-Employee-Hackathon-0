"""
Base Watcher Pattern Implementation
Following the constitution's BaseWatcher pattern specification
"""
import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod


class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Abstract method to check for updates in the monitored source
        Returns list of items that need processing
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Abstract method to create an action file from the detected item
        Returns path to the created action file
        """
        pass

    def run(self):
        """Main execution loop for the watcher"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')
            time.sleep(self.check_interval)


def setup_logging():
    """Configure logging for the watcher system"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )