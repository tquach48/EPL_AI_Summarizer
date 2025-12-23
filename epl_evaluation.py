# CSCI4152/6509 Fall 2025
# Program: EPL Evaluation Module
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Evaluates the summarizations based on ROUGE,
# coverage and hallucination rate

from rouge_score import rouge_scorer
from collections import Counter
import re

# --------------------------------------------------
# Utility
# --------------------------------------------------

def normalize(text: str) -> str:
    return text.lower().strip() if text else ""


# --------------------------------------------------
# ROUGE Evaluation
# --------------------------------------------------

def evaluate_rouge(entries):
    scorer = rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL"],
        use_stemmer=True
    )

    scores = {"rouge1": [], "rouge2": [], "rougeL": []}

    for entry in entries:
        reference = normalize(entry.get("raw_text"))
        summary = normalize(entry.get("summary"))

        if not reference or not summary:
            continue

        result = scorer.score(reference, summary)
        for k in scores:
            scores[k].append(result[k].fmeasure)

    return {k: round(sum(v)/len(v),4) if v else 0.0 for k,v in scores.items()}


# --------------------------------------------------
# Coverage Evaluation
# --------------------------------------------------

def evaluate_coverage(entry):
    summary = normalize(entry.get("summary"))

    coverage = {
        "events": False
    }

    # Check if at least one event is mentioned in summary
    events = entry.get("events", [])
    for e in events:
        if normalize(e) in summary:
            coverage["events"] = True
            break

    return coverage

def evaluate_dataset_coverage(entries):
    totals = Counter()
    n = len(entries)

    for entry in entries:
        c = evaluate_coverage(entry)
        for k, v in c.items():
            totals[k] += int(v)

    return {k: round(totals[k]/n,4) if n else 0.0 for k in totals}


# --------------------------------------------------
# Hallucination Detection
# --------------------------------------------------

def extract_known_persons(entry):
    """Return a set of known PERSON names from entity extraction."""
    entities = entry.get("entities", [])
    persons = {normalize(e[0]) for e in entities if e[1] == "PERSON"}
    return persons

def evaluate_hallucination(entry):
    summary = entry.get("summary", "")
    known_persons = extract_known_persons(entry)

    # Simple regex to extract Capitalized Firstname Lastname in summary
    candidate_names = re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", summary)
    hallucinated = [name for name in candidate_names if normalize(name) not in known_persons]
    return list(set(hallucinated))


# --------------------------------------------------
# Full Evaluation Runner
# --------------------------------------------------

def run_full_evaluation(entries, verbose=True):
    report = {}

    report["rouge"] = evaluate_rouge(entries)
    report["coverage"] = evaluate_dataset_coverage(entries)

    # Count entries with at least one hallucination
    hallucinated_entries = sum(
        1 for e in entries if evaluate_hallucination(e)
    )

    report["hallucination_rate"] = round(hallucinated_entries / len(entries), 4) if entries else 0.0

    if verbose:
        print("✔ Evaluation complete")
        print("ROUGE:", report["rouge"])
        print("Coverage:", report["coverage"])
        print("Hallucination rate:", report["hallucination_rate"])

    return report
