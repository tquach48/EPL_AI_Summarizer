# CSCI4152/6509 Fall 2025
# Program: Named Entity Recognition
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Extracts named entities (players, teams, etc.) from match reports
# using NLTK, returning structured lists for further analysis.


import nltk

# Ensure NLTK resources are downloaded
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")


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
