import os
import sys
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.config import Config

sys.path.insert(0, str(Path(__file__).parent.parent / "python-hslog"))
from hslog import LogParser


class LogFileHandler(FileSystemEventHandler):
    def __init__(self, log_path: Path, on_new_line: Callable[[str], None]):
        self.log_path = log_path
        self.on_new_line = on_new_line
        self.file_position = 0
        if log_path.exists():
            self.file_position = log_path.stat().st_size

    def on_modified(self, event):
        if event.src_path == str(self.log_path):
            self.read_new_lines()

    def read_new_lines(self):
        try:
            with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(self.file_position)
                new_lines = f.readlines()
                self.file_position = f.tell()
                for line in new_lines:
                    line = line.strip()
                    if line:
                        self.on_new_line(line)
        except Exception as e:
            print(f"Error reading log file: {e}")


class LogMonitor:
    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or Config.LOG_PATH
        self.parser = LogParser()
        self.observer = None
        self.event_handler = None
        self.on_packet_tree_callback = None

    def set_on_packet_tree_callback(self, callback: Callable):
        self.on_packet_tree_callback = callback

    def start(self):
        print(f"Starting log monitor on: {self.log_path}")
        self.event_handler = LogFileHandler(self.log_path, self._on_new_line)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, str(self.log_path.parent), recursive=False)
        self.observer.start()

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def _on_new_line(self, line: str):
        try:
            self.parser.read_line(line)
            if self.parser.games:
                latest_game = self.parser.games[-1]
                if self.on_packet_tree_callback:
                    self.on_packet_tree_callback(latest_game)
        except Exception as e:
            print(f"Error parsing line: {e}")
