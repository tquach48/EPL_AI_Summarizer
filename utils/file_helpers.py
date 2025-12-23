# CSCI4152/6509 Fall 2025
# Program: File Helpers
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Provides helper functions for reading/writing JSON files
# and other file operations in the EPL summarization pipeline.


import json
import os


def load_json(filename):
    """Load JSON data from a file."""
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, filename):
    """Save JSON data to a file with pretty formatting."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"💾 Saved to {filename}")


def append_to_json(entry, filename):
    """Append a single entry to a JSON file (creates if not exists)."""
    data = load_json(filename)
    data.append(entry)
    save_json(data, filename)
