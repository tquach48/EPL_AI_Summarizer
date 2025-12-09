import json
import re
import nltk
from transformers import pipeline
from sklearn.model_selection import train_test_split

# --------------------------
# NLTK SETUP
# --------------------------
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")

# --------------------------
# LOAD MODELS
# --------------------------
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# --------------------------
# ENTITY EXTRACTION
# --------------------------
def extract_entities(text):
    """
    Uses NLTK to extract named entities from text.
    Returns a list of (entity, type) tuples.
    """
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

# --------------------------
# EVENT EXTRACTION
# --------------------------
def extract_events(text):
    """
    Extracts simple goal-related events from match text.
    """
    if not text:
        return []

    events = []
    goal_pattern = r"(\d+'\s*)?([^\.]*goal[^\.]*)"
    for m in re.finditer(goal_pattern, text, flags=re.I):
        events.append(m.group(0))
    return events

# --------------------------
# SUMMARIZATION
# --------------------------
def summarize_text(text):
    """
    Summarizes text paragraph-wise first, then
    combines paragraph summaries into a final summary.
    """
    if not text or len(text.strip()) < 50:
        return text or ""

    paragraphs = [p for p in text.split("\n") if p.strip()]
    paragraph_summaries = []

    for p in paragraphs:
        input_len = len(p.split())  # word count
        max_len = min(60, input_len)
        min_len = max(5, int(max_len * 0.5))  # minimum 5 words
        min_len = min(min_len, max_len)       # ensure min <= max

        try:
            summary = summarizer(p, max_length=max_len, min_length=min_len, do_sample=False)[0]['summary_text']
        except Exception:
            summary = p
        paragraph_summaries.append(summary)

    combined_summary = " ".join(paragraph_summaries)

    final_max_len = min(200, len(combined_summary.split()))
    final_min_len = max(10, int(final_max_len * 0.5))
    final_min_len = min(final_min_len, final_max_len)  # ensure min <= max

    try:
        final_summary = summarizer(combined_summary, max_length=final_max_len, min_length=final_min_len, do_sample=False)[0]['summary_text']
    except Exception:
        final_summary = combined_summary

    return final_summary

# --------------------------
# PROCESS SINGLE ENTRY
# --------------------------
def process_entry(entry):
    raw = entry.get("report", "")
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
