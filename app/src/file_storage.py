import json

class EventFileManager:
    FILE_PATH = "events.json"

    def read_events_from_file(self):
        try:
            with open(self.FILE_PATH, "r") as file:
                events = json.load(file)
        except FileNotFoundError:
            return []
        return events

    def write_events_to_file(self, events):
        with open(self.FILE_PATH, "w") as file:
            json.dump(events, file, indent=4)
