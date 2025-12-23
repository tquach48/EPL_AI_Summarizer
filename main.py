# CSCI4152/6509 Fall 2025
# Program: EPL Summarization Pipeline
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Main entry point for processing EPL match data, including
# train/test split, hybrid summarization, injury detection, key players,
# event extraction, and saving processed results.


import json
from sklearn.model_selection import train_test_split

# --- NLP modules ---
from nlp.summarization import hybrid_summary, summarize_text
from nlp.entities import extract_entities
from nlp.events import extract_events

# --- Analysis modules ---
from analysis.injuries import detect_injuries, attach_players_to_injuries
from analysis.narrative import classify_match
from analysis.players import detect_key_players

# --- Templates ---
from templates.match_template import build_template_summary

# --- Utilities ---
from utils.logging_helpers import log_done
from utils.file_helpers import save_json


def process_entry(entry):
    """
    Process a single match entry:
    - Extract entities
    - Detect injuries and attach players
    - Classify match narrative
    - Detect key players
    - Extract events
    - Build hybrid + raw summaries
    """
    raw_text = entry.get("report", "")
    entities = extract_entities(raw_text)

    # Injuries
    injury_sents = detect_injuries(raw_text)
    injuries = attach_players_to_injuries(injury_sents, entities)

    # Key players
    key_players = detect_key_players(entry)

    # Hybrid summary
    summary_hybrid = hybrid_summary(entry)
    summary_raw = summarize_text(raw_text)

    # Events
    events = extract_events(raw_text)

    # Match narrative
    match_type = classify_match(entry)

    result = {
        "match": f"{entry['home_team']} vs {entry['away_team']}",
        "home_team": entry["home_team"],
        "away_team": entry["away_team"],
        "match_type": match_type,
        "key_players": key_players,
        "injuries": injuries,
        "events": events,
        "hybrid_summary": summary_hybrid,
        "raw_summary": summary_raw,
        "raw_text": raw_text,  # Needed for evaluation
    }

    log_done(result["match"], match_type, injuries=bool(injuries))
    return result


def main(json_file="premier_league_results.json", test_size=0.1, random_state=42):
    """
    Main orchestrator:
    - Loads raw data
    - Splits into train/test
    - Processes each entry
    - Saves processed JSON files
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    train_data, test_data = train_test_split(
        data, test_size=test_size, random_state=random_state, shuffle=True
    )

    print(f"Training entries: {len(train_data)}")
    print(f"Testing entries: {len(test_data)}\n")

    processed_train = [process_entry(e) for e in train_data]
    processed_test = [process_entry(e) for e in test_data]

    save_json(processed_train, "train_processed.json")
    save_json(processed_test, "test_processed.json")

    print("\n🏁 All matches summarized successfully.")


if __name__ == "__main__":
    main()
