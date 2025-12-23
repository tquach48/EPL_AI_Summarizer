# CSCI4152/6509 Fall 2025
# Program: Match Narrative Classification
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Classifies matches into narrative categories such as
# dominant win, narrow win, draw, based on scores and stats.


from .stats import get_stat, parse_float


def classify_match(entry):
    """
    Classifies match outcome as:
    - Draw
    - Narrow win
    - Convincing win
    - Dominant win
    """
    home = entry["home_team"]
    away = entry["away_team"]
    score = entry["final_score"]

    home_goals = int(score["home"])
    away_goals = int(score["away"])

    xg_home, xg_away = get_stat(entry.get("stats"), "XG")
    xg_home = parse_float(xg_home)
    xg_away = parse_float(xg_away)

    # Draw
    if home_goals == away_goals:
        return "Draw"

    winner = home if home_goals > away_goals else away
    margin = abs(home_goals - away_goals)

    # Dominance
    if xg_home and xg_away and abs(xg_home - xg_away) >= 1.5:
        return f"Dominant win for {winner}"

    # Narrow win
    if margin == 1:
        return f"Narrow win for {winner}"

    return f"Convincing win for {winner}"
