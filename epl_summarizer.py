import json
import re
import spacy
from transformers import pipeline
from sklearn.model_selection import train_test_split

# --------------------------
# LOAD MODELS
# --------------------------
nlp = spacy.load("en_core_web_trf")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# --------------------------
# ENTITY EXTRACTION
# --------------------------
def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

# --------------------------
# EVENT EXTRACTION
# --------------------------
def extract_events(text):
    events = []
    goal_pattern = r"(\d+'\s*)?([^\.]*goal[^\.]*)"
    for m in re.finditer(goal_pattern, text, flags=re.I):
        events.append(m.group(0))
    return events

# --------------------------
# SUMMARIZATION
# --------------------------
def summarize_text(text):
    if len(text) < 100:
        return text  # avoid crashing for short text
    summary = summarizer(
        text,
        max_length=200,
        min_length=60,
        do_sample=False
    )[0]['summary_text']
    return summary

# --------------------------
# PROCESS SINGLE ENTRY
# --------------------------
def process_entry(entry):
    raw = entry.get("match_report", "")
    return {
        "raw_text": raw,
        "entities": extract_entities(raw),
        "events": extract_events(raw),
        "summary": summarize_text(raw)
    }

# --------------------------
# MAIN PROCESSING
# --------------------------
def main(json_file="premier_league_results.json"):
    # Load dataset
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Split into train/test
    train_data, test_data = train_test_split(
        data,
        test_size=0.10,   # 10% test
        random_state=42,
        shuffle=True
    )

    print(f"Training entries: {len(train_data)}")
    print(f"Testing entries: {len(test_data)}")

    # Process both splits
    processed_train = [process_entry(entry) for entry in train_data]
    processed_test = [process_entry(entry) for entry in test_data]

    # Save outputs
    with open("train_processed.json", "w", encoding="utf-8") as f:
        json.dump(processed_train, f, indent=4, ensure_ascii=False)

    with open("test_processed.json", "w", encoding="utf-8") as f:
        json.dump(processed_test, f, indent=4, ensure_ascii=False)

    print("\nSaved:")
    print(" - train_processed.json")
    print(" - test_processed.json")


if __name__ == "__main__":
    main()
