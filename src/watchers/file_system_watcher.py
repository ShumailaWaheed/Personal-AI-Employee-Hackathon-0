"""
File System Watcher Implementation
Monitors the vault's Inbox directory for new files and moves them to Needs_Action
"""
import time
import shutil
from pathlib import Path
from typing import List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .base_watcher import BaseWatcher


class FileCreatedHandler(FileSystemEventHandler):
    """Handles file creation events in the watched directory"""
    def __init__(self, callback):
        self.callback = callback
        super().__init__()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self.callback(event.src_path)


class FileSystemWatcher(BaseWatcher):
    def __init__(self, vault_path: str, check_interval: int = 5):
        super().__init__(vault_path, check_interval)
        self.observer = Observer()
        self.new_files = []

        # Ensure directories exist
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.needs_action.mkdir(exist_ok=True)
        self.done.mkdir(exist_ok=True)

    def start_observer(self):
        """Start the file system observer"""
        event_handler = FileCreatedHandler(self._handle_new_file)
        self.observer.schedule(event_handler, str(self.inbox), recursive=False)
        self.observer.start()

    def stop_observer(self):
        """Stop the file system observer"""
        self.observer.stop()
        self.observer.join()

    def _handle_new_file(self, file_path: str):
        """Handle a newly created file"""
        self.new_files.append(file_path)
        self.logger.info(f"Detected new file: {file_path}")

    def check_for_updates(self) -> List[str]:
        """
        Check for new files in the Inbox directory
        Returns list of file paths that need processing
        """
        # Process any files detected by the observer
        files_to_process = self.new_files[:]
        self.new_files.clear()

        # Also scan for any files that might have been missed
        for file_path in self.inbox.glob("*.md"):
            file_str = str(file_path)
            if file_str not in files_to_process:
                files_to_process.append(file_str)

        return files_to_process

    def create_action_file(self, item: str) -> Path:
        """
        Move the detected file from Inbox to Needs_Action
        Returns path to the moved file
        """
        source_path = Path(item)
        dest_path = self.needs_action / source_path.name

        # Move file from Inbox to Needs_Action
        shutil.move(str(source_path), str(dest_path))

        self.logger.info(f"Moved {source_path.name} from Inbox to Needs_Action")
        return dest_path

    def run(self):
        """Override run method to use file system observer"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.start_observer()

        try:
            while True:
                # Check for any new files that need processing
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)

                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("Stopping file system watcher...")
            self.stop_observer()