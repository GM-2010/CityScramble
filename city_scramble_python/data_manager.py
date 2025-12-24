import json
import os

class DataManager:
    """
    Centralized manager for loading and saving game data (settings, scores, etc.).
    """
    def __init__(self, filename="city_scramble_score.json"):
        self.filename = filename
        self.data = {}
        self.load()

    def load(self):
        """Load data from JSON file. If file not found or error, start empty."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.data = json.load(f)
                    print(f"[DataManager] Data loaded from {self.filename}")
            except Exception as e:
                print(f"[DataManager] Error loading data: {e}")
                self.data = {}
        else:
            print(f"[DataManager] No save file found at {self.filename}, starting fresh.")
            self.data = {}

    def save(self):
        """Save current data to JSON file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.data, f, indent=4)
                # print(f"[DataManager] Data saved.") # Optional, can be spammy
        except Exception as e:
            print(f"[DataManager] Error saving data: {e}")

    def get(self, key, default=None):
        """Get a value by key, returning default if not found."""
        return self.data.get(key, default)

    def set(self, key, value):
        """Set a value by key. Does NOT auto-save (call save() explicitly)."""
        self.data[key] = value

    def set_and_save(self, key, value):
        """Set a value and save immediately."""
        self.data[key] = value
        self.save()
