# CSCI4152/6509 Fall 2025
# Program: NLP Summarization
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Implements BART-based summarization and hybrid summary generation
# for EPL match reports. Provides paragraph-wise summarization and template refinement.


from transformers import pipeline

# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def hybrid_summary(entry):
    """
    Builds a hybrid summary using template + abstractive refinement.
    """
    from templates.match_template import build_template_summary

    template = build_template_summary(entry)

    try:
        refined = summarizer(
            template,
            max_length=60,
            min_length=25,
            do_sample=False
        )[0]["summary_text"]
        return refined
    except Exception:
        return template


def summarize_text(text):
    """
    Summarizes text paragraph-wise first, then combines into final summary.
    """
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
        final_summary = summarizer(
            combined_summary,
            max_length=final_max_len,
            min_length=final_min_len,
            do_sample=False
        )[0]['summary_text']
    except Exception:
        final_summary = combined_summary

    return final_summary
