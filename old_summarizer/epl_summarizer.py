# CSCI4152/6509 Fall 2025
# Program: EPL Summarizer Orchestration
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Orchestrates the end-to-end EPL summarization pipeline.

import json
import re
import nltk
from transformers import pipeline
from sklearn.model_selection import train_test_split

# -------------------------------------------------------------------
# INJURY LEXICON
# -------------------------------------------------------------------
INJURY_TRIGGERS = [
    "forced off", "pulled up", "went down", "unable to continue",
    "could not continue", "limped off", "left the field", "took a knock",
    "picked up a knock", "injury concern", "problem for", "fitness concern",
    "went straight down", "received treatment", "required treatment"
]

MEDICAL_TERMS = [
    "stretcher", "physio", "medical staff", "treatment", "ice pack", "bandage"
]

SUBSTITUTION_PHRASES = [
    "was replaced by", "substituted", "came off", "forced substitution"
]

# -------------------------------------------------------------------
# NLTK SETUP
# -------------------------------------------------------------------
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")

# -------------------------------------------------------------------
# LOAD MODELS
# -------------------------------------------------------------------
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# -------------------------------------------------------------------
# INJURY DETECTION
# -------------------------------------------------------------------
def detect_injuries(text):
    if not text:
        return []
    injury_events = []
    sentences = nltk.sent_tokenize(text)
    for sent in sentences:
        sent_lower = sent.lower()
        score = 0
        if any(trigger in sent_lower for trigger in INJURY_TRIGGERS):
            score += 2
        if any(term in sent_lower for term in MEDICAL_TERMS):
            score += 1
        if any(sub in sent_lower for sub in SUBSTITUTION_PHRASES):
            score += 1
        if score >= 2:
            injury_events.append(sent)
    return injury_events

def attach_players_to_injuries(injury_sentences, entities):
    players = [e[0] for e in entities if e[1] == "PERSON"]
    player_injuries = []
    for sent in injury_sentences:
        involved = [p for p in players if p in sent]
        player_injuries.append({"sentence": sent, "players": involved if involved else ["Unknown"]})
    return player_injuries

# -------------------------------------------------------------------
# STAT EXTRACTION HELPERS
# -------------------------------------------------------------------
def get_stat(stats, stat_name):
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
    return float(val.replace("%", "").strip())

def parse_float(val):
    if not val:
        return None
    try:
        return float(val)
    except:
        return None

# -------------------------------------------------------------------
# MATCH NARRATIVE
# -------------------------------------------------------------------
def classify_match(entry):
    home = entry["home_team"]
    away = entry["away_team"]
    score = entry["final_score"]
    home_goals = int(score["home"])
    away_goals = int(score["away"])
    xg_home, xg_away = get_stat(entry.get("stats"), "XG")
    xg_home = parse_float(xg_home)
    xg_away = parse_float(xg_away)
    if home_goals == away_goals:
        return "Draw"
    winner = home if home_goals > away_goals else away
    margin = abs(home_goals - away_goals)
    if xg_home and xg_away and abs(xg_home - xg_away) >= 1.5:
        return f"Dominant win for {winner}"
    if margin == 1:
        return f"Narrow win for {winner}"
    return f"Convincing win for {winner}"

# -------------------------------------------------------------------
# PLAYER IMPACT
# -------------------------------------------------------------------
def detect_key_players(entry):
    scorer_counts = {}
    for goal in entry.get("scorers", []):
        player = goal["player"]
        scorer_counts[player] = scorer_counts.get(player, 0) + 1
    key_players = []
    for player, goals in scorer_counts.items():
        if goals >= 2:
            key_players.append(player)
    if not key_players and scorer_counts:
        key_players.append(max(scorer_counts, key=scorer_counts.get))
    return key_players

# -------------------------------------------------------------------
# TEMPLATE SUMMARY
# -------------------------------------------------------------------
def build_template_summary(entry):
    home = entry["home_team"]
    away = entry["away_team"]
    score = entry["final_score"]
    home_goals = score["home"]
    away_goals = score["away"]
    xg_home, xg_away = get_stat(entry.get("stats"), "XG")
    shots_home, shots_away = get_stat(entry.get("stats"), "Shots On Target")
    scorers = detect_key_players(entry)
    sentence_1 = f"{home} beat {away} {home_goals}-{away_goals}."
    sentence_2_parts = []
    if scorers:
        if len(scorers) == 1:
            sentence_2_parts.append(f"{scorers[0]} was the standout performer.")
        else:
            sentence_2_parts.append(f"Key contributions came from {', '.join(scorers[:-1])} and {scorers[-1]}.")
    if xg_home and xg_away:
        sentence_2_parts.append(f"They led on xG ({xg_home} vs {xg_away}).")
    if shots_home and shots_away:
        sentence_2_parts.append(f"Shots on target finished {shots_home} to {shots_away}.")
    sentence_2 = " ".join(sentence_2_parts)
    return f"{sentence_1} {sentence_2}"

# -------------------------------------------------------------------
# HYBRID SUMMARY
# -------------------------------------------------------------------
def hybrid_summary(entry):
    template = build_template_summary(entry)
    try:
        refined = summarizer(template, max_length=60, min_length=25, do_sample=False)[0]["summary_text"]
        return refined
    except:
        return template

# -------------------------------------------------------------------
# ENTITY EXTRACTION
# -------------------------------------------------------------------
def extract_entities(text):
    if not text:
        return []
    sentences = nltk.sent_tokenize(text)
    entities = []
    for sent in sentences:
        words = nltk.word_tokenize(sent)
        pos_tags = nltk.pos_tag(words)
        chunks = nltk.ne_chunk(pos_tags, binary=False)
        for chunk in chunks:
            if hasattr(chunk, "label"):
                entity_name = " ".join(c[0] for c in chunk)
                entities.append((entity_name, chunk.label()))
    return entities

# -------------------------------------------------------------------
# EVENT EXTRACTION
# -------------------------------------------------------------------
def extract_events(text):
    if not text:
        return []
    events = []
    goal_pattern = r"(\d+'\s*)?([^\.]*goal[^\.]*)"
    for m in re.finditer(goal_pattern, text, flags=re.I):
        events.append(m.group(0))
    return events

# -------------------------------------------------------------------
# SUMMARIZATION
# -------------------------------------------------------------------
def summarize_text(text):
    if not text or len(text.strip()) < 50:
        return text or ""
    paragraphs = [p for p in text.split("\n") if p.strip()]
    paragraph_summaries = []
    for p in paragraphs:
        input_len = len(p.split())
        max_len = min(60, input_len)
        min_len = max(5, int(max_len * 0.5))
        min_len = min(min_len, max_len)
        try:
            summary = summarizer(p, max_length=max_len, min_length=min_len, do_sample=False)[0]['summary_text']
        except Exception:
            summary = p
        paragraph_summaries.append(summary)
    combined_summary = " ".join(paragraph_summaries)
    final_max_len = min(200, len(combined_summary.split()))
    final_min_len = max(10, int(final_max_len * 0.5))
    final_min_len = min(final_min_len, final_max_len)
    try:
        final_summary = summarizer(combined_summary, max_length=final_max_len, min_length=final_min_len, do_sample=False)[0]['summary_text']
    except Exception:
        final_summary = combined_summary
    return final_summary

# -------------------------------------------------------------------
# HELPER LOGGER
# -------------------------------------------------------------------
def log_done(match_name, match_type=None, injuries=None):
    msg = f"✅ Processed: {match_name}"
    if match_type:
        msg += f" | {match_type}"
    if injuries:
        msg += f" | Injuries detected"
    print(msg)

# -------------------------------------------------------------------
# PROCESS SINGLE ENTRY
# -------------------------------------------------------------------
def process_entry(entry):
    raw = entry.get("report", "")
    entities = extract_entities(raw)
    injury_sents = detect_injuries(raw)
    injuries = attach_players_to_injuries(injury_sents, entities)
    result = {
        "match": f"{entry['home_team']} vs {entry['away_team']}",
        "match_type": classify_match(entry),
        "key_players": detect_key_players(entry),
        "injuries": injuries,
        "events": extract_events(raw),
        "hybrid_summary": hybrid_summary(entry),
        "raw_summary": summarize_text(raw)
    }
    log_done(match_name=result["match"], match_type=result["match_type"], injuries=bool(injuries))
    return result

# -------------------------------------------------------------------
# MAIN PROCESSING
# -------------------------------------------------------------------
def main(json_file="premier_league_results.json"):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    train_data, test_data = train_test_split(data, test_size=0.10, random_state=42, shuffle=True)
    print(f"Training entries: {len(train_data)}")
    print(f"Testing entries: {len(test_data)}\n")
    processed_train = [process_entry(e) for e in train_data]
    processed_test = [process_entry(e) for e in test_data]
    with open("output/train_processed.json", "w", encoding="utf-8") as f:
        json.dump(processed_train, f, indent=4, ensure_ascii=False)
    with open("output/test_processed.json", "w", encoding="utf-8") as f:
        json.dump(processed_test, f, indent=4, ensure_ascii=False)
    print("\n🏁 All matches summarized successfully.")

# -------------------------------------------------------------------
# RUN SCRIPT
# -------------------------------------------------------------------
if __name__ == "__main__":
    main()
