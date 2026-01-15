# EPL Match Text Summarization

This project implements a hybrid Natural Language Processing (NLP) pipeline for generating concise, *at-a-glance* summaries of English Premier League (EPL) soccer matches. The system processes unstructured match reports and produces short, human-readable summaries designed for rapid consumption by casual fans and readers.

The project was developed as part of **CSCI 4152 – Natural Language Processing** at **Dalhousie University**.

---

## Project Overview

Modern sports media produces an overwhelming volume of textual content per matchday. While detailed match reports are valuable, they are often too long for readers who simply want to understand the outcome and key moments of a game quickly. This project addresses that gap by generating short summaries that capture the essential information of an EPL match without reconstructing the full narrative.

To achieve this, the system combines:

* Rule-based linguistic extraction for factual grounding
* Lightweight Named Entity Recognition (NER)
* Event-oriented heuristics
* Transformer-based abstractive summarization

This hybrid approach balances conciseness, readability, and factual accuracy while reducing the risk of hallucination.

---

## Key Features

* Automated scraping of EPL match reports
* Linguistic extraction of players, teams, and events
* Hybrid summarization (template-based + abstractive refinement)
* Extreme short-form summaries for *at-a-glance* consumption
* Evaluation using ROUGE, coverage metrics, and hallucination detection
* Qualitative human review from soccer fans

---

## Project Structure

```
epl_project/
│
├── analysis/
│   ├── players.py          # Key player detection
│   ├── stats.py            # Match statistics extraction
│   └── events.py           # Rule-based event extraction
│
├── summarization/
│   ├── abstractive.py      # Transformer-based summarization
│   ├── hybrid.py           # Hybrid summarization pipeline
│   └── templates.py        # Template-based summary construction
│
├── scraper/
│   └── scrape_matches.py   # Selenium-based EPL scraper
│
├── evaluation/
│   ├── rouge_eval.py       # ROUGE scoring
│   ├── coverage_eval.py    # Information coverage metrics
│   └── hallucination.py    # Entity-based hallucination detection
│
├── data/
│   ├── raw/                # Raw scraped match reports
│   └── processed/          # Processed JSON outputs
│
├── eval_runner.py          # End-to-end evaluation script
├── requirements.txt
└── README.md
```

---

## Methodology Summary

1. **Data Collection**
   Match reports are scraped from the official Premier League website using Selenium to handle dynamic content.

2. **Linguistic Extraction**

   * Sentence tokenization and preprocessing
   * Named Entity Recognition for player names
   * Rule-based pattern matching for events and injuries

3. **Summarization**

   * Hierarchical abstractive summarization using `facebook/bart-large-cnn`
   * Template-based summaries constructed from verified metadata
   * Optional abstractive refinement under strict length constraints

4. **Evaluation**

   * ROUGE-1, ROUGE-2, ROUGE-L
   * Event and entity coverage
   * Hallucination rate based on unsupported entity mentions
   * Qualitative human review

---

## Example Output

**Generated Summary:**

> *West Ham struggled to deal with crosses early on and nearly fell further behind after the break. They responded through Bowen, but defensive lapses proved costly. Crystal Palace were boosted by the return of Adam Wharton and held on to secure the result.*

This summary is intended to be read in seconds and paired with a scoreboard or match interface.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/epl-match-summarization.git
cd epl-match-summarization
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Pipeline

To generate summaries:

```bash
python summarization/hybrid.py
```

To evaluate summaries:

```bash
python eval_runner.py
```

---

## Evaluation Results (Summary)

* **ROUGE-1:** 0.284
* **ROUGE-2:** 0.1935
* **ROUGE-L:** 0.1895
* **Hallucination Rate:** 0.25

Human reviewers reported that summaries were coherent and accurately reflected matches they had watched, supporting the practical usefulness of the system despite modest automatic scores.

---

## Limitations

* Rule-based extraction may miss paraphrased or implicit events
* Abstractive model is not fine-tuned on sports-specific data
* ROUGE underestimates quality for extreme short-form summaries
* Hallucination detection relies on heuristic entity matching

---

## Future Work

* Event-guided neural summarization
* Domain-specific fine-tuning on sports datasets
* Improved event-level coverage metrics
* Larger-scale human evaluation
* Integration with visual match data (scoreboards, highlights)

---

## Author

**Terry Quach**
CSCI 4152 – Natural Language Processing
Dalhousie University

---

If you want, I can also:

* Shorten this for a **GitHub-friendly README**
* Make a **more formal course-submission version**
* Add **badges, diagrams, or usage screenshots**

Just tell me 👍
