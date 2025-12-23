# CSCI4152/6509 Fall 2025
# Program: Event Extraction
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Detects and extracts goal and other key match events from
# match text, returning structured event information.

import re


def extract_events(text):
    """
    Extracts simple goal-related events from match text.
    Returns a list of strings.
    """
    if not text:
        return []

    events = []
    goal_pattern = r"(\d+'\s*)?([^\.]*goal[^\.]*)"

    for m in re.finditer(goal_pattern, text, flags=re.I):
        events.append(m.group(0))

    return events
