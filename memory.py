import json
import os

MEMORY_FILE = "user_memory.json"

def load_memory():
    """Load all user memory from the JSON file (or return empty dict if not found)."""
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory: dict):
    """Save the full memory dict back to the JSON file."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

def get_user_preferences(user_id: str):
    """Return the preferences dict for this user id."""
    memory = load_memory()
    return memory.get(user_id, {}).get("preferences", {})

def update_user_preferences(user_id: str, new_prefs: dict):
    """Merge new_prefs into the user's existing preferences and save."""
    memory = load_memory()
    if user_id not in memory:
        memory[user_id] = {"preferences": {}}
    memory[user_id]["preferences"].update(new_prefs)
    save_memory(memory)
