# CSCI4152/6509 Fall 2025
# Program: Main Evaluation Runner
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Loads processed match data and runs the full evaluation
# pipeline using epl_evaluation.py, printing ROUGE, coverage, and
# hallucination metrics.


import json
from epl_evaluation import run_full_evaluation

# Load processed dataset
with open("output/test_processed.json", "r", encoding="utf-8") as f:
    entries = json.load(f)

# Run evaluation
report = run_full_evaluation(entries, verbose=True)

# Optionally save report
with open("output/evaluation_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=4)
