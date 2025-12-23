# CSCI4152/6509 Fall 2025
# Program: Template-based Summary Builder
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Generates structured template summaries for EPL matches
# using scorelines, key stats, and player performance data.


from analysis.stats import get_stat
from analysis.players import detect_key_players



def build_template_summary(entry):
    """
    Builds a template summary based on:
    - Final score
    - xG and shots stats
    - Key player performances
    """
    home = entry["home_team"]
    away = entry["away_team"]
    score = entry["final_score"]

    home_goals = score["home"]
    away_goals = score["away"]

    # Extract top stats
    xg_home, xg_away = get_stat(entry.get("stats"), "XG")
    shots_home, shots_away = get_stat(entry.get("stats"), "Shots On Target")

    # Detect key players
    key_players = detect_key_players(entry)

    # First sentence: result
    sentence_1 = f"{home} beat {away} {home_goals}-{away_goals}."

    # Second sentence: player impact and stats
    sentence_2_parts = []

    if key_players:
        if len(key_players) == 1:
            sentence_2_parts.append(f"{key_players[0]} was the standout performer.")
        else:
            sentence_2_parts.append(
                f"Key contributions came from {', '.join(key_players[:-1])} and {key_players[-1]}."
            )

    if xg_home and xg_away:
        sentence_2_parts.append(f"They led on xG ({xg_home} vs {xg_away}).")

    if shots_home and shots_away:
        sentence_2_parts.append(f"Shots on target finished {shots_home} to {shots_away}.")

    sentence_2 = " ".join(sentence_2_parts)

    return f"{sentence_1} {sentence_2}"
