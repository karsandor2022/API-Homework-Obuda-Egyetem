import json
import os

class EventFileManager:
    FILE_PATH = "event.json"  # file already exists in project root

    @classmethod
    def read_events_from_file(cls):
        if not os.path.exists(cls.FILE_PATH):
            return []
        try:
            with open(cls.FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    @classmethod
    def write_events_to_file(cls, events):
        with open(cls.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=4)