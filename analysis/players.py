# CSCI4152/6509 Fall 2025
# Program: Key Player Detection
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Detects key players in a match based on goals, assists,
# and other metrics to highlight player impact.


def detect_key_players(entry):
    """
    Returns list of key players in a match based on goal contribution.
    """
    scorer_counts = {}

    for goal in entry.get("scorers", []):
        player = goal["player"]
        scorer_counts[player] = scorer_counts.get(player, 0) + 1

    key_players = []

    # Players with >=2 goals are automatically key
    for player, goals in scorer_counts.items():
        if goals >= 2:
            key_players.append(player)

    # Fallback: top scorer if none scored >=2
    if not key_players and scorer_counts:
        key_players.append(max(scorer_counts, key=scorer_counts.get))

    return key_players
