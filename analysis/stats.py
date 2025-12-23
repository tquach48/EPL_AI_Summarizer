# CSCI4152/6509 Fall 2025
# Program: Stat Parsing Helpers
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Provides helper functions to parse and extract
# match statistics (e.g., xG, shots on target) from structured data.


def get_stat(stats, stat_name):
    """
    Safely extract a stat from any section in the stats dictionary.
    Returns (home_val, away_val) or (None, None)
    """
    if not stats:
        return None, None

    for section in stats.values():
        for row in section:
            if row["stat"].lower() == stat_name.lower():
                return row["home"], row["away"]
    return None, None


def parse_percentage(val):
    if not val:
        return None
    try:
        return float(val.replace("%", "").strip())
    except ValueError:
        return None


def parse_float(val):
    if not val:
        return None
    try:
        return float(val)
    except ValueError:
        return None
