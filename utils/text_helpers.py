# CSCI4152/6509 Fall 2025
# Program: Text Helpers
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Provides utility functions for text processing, including
# normalization, cleaning, tokenization, and other helper methods

def parse_float(val):
    """Safely parse a float from a string."""
    if not val:
        return None
    try:
        return float(val)
    except ValueError:
        return None


def parse_percentage(val):
    """Convert percentage string to float."""
    if not val:
        return None
    try:
        return float(val.replace("%", "").strip())
    except ValueError:
        return None


def clean_whitespace(text):
    """Strip extra spaces and normalize newlines."""
    if not text:
        return ""
    return " ".join(text.split())
