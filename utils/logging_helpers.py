# CSCI4152/6509 Fall 2025
# Program: Logging Helpers
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Provides helper functions for logging progress,
# completion messages, and other runtime logs during summarization.



def log_done(match_name, match_type=None, injuries=None):
    """
    Logs a summary of a processed match.
    """
    msg = f" Processed: {match_name}"
    print(msg)


def log_progress(current, total, prefix="Progress"):
    """
    Logs processing progress.
    """
    print(f"   → {prefix}: {current}/{total}")
