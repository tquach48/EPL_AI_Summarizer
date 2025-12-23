# CSCI4152/6509 Fall 2025
# Program: Injury Detection
# Author: Terry Quach, B00919525, hn886911@dal.ca
# Description: Detects injuries from match reports, including implied injuries,
# links them to players, and returns structured injury data.

import nltk

# Lexicon of injury triggers, medical terms, and substitution phrases
INJURY_TRIGGERS = [
    "forced off", "pulled up", "went down", "unable to continue",
    "could not continue", "limped off", "left the field",
    "took a knock", "picked up a knock", "injury concern",
    "problem for", "fitness concern", "went straight down",
    "received treatment", "required treatment"
]

MEDICAL_TERMS = [
    "stretcher", "physio", "medical staff", "treatment", "ice pack", "bandage"
]

SUBSTITUTION_PHRASES = [
    "was replaced by", "substituted", "came off", "forced substitution"
]


def detect_injuries(text):
    """
    Detects implied injury events from match reports.
    Returns a list of injury-related sentences.
    """
    if not text:
        return []

    injury_events = []
    sentences = nltk.sent_tokenize(text)

    for sent in sentences:
        sent_lower = sent.lower()
        score = 0

        # Strong signals
        if any(trigger in sent_lower for trigger in INJURY_TRIGGERS):
            score += 2

        # Medium signals
        if any(term in sent_lower for term in MEDICAL_TERMS):
            score += 1

        if any(sub in sent_lower for sub in SUBSTITUTION_PHRASES):
            score += 1

        # Threshold to consider as injury
        if score >= 2:
            injury_events.append(sent)

    return injury_events


def attach_players_to_injuries(injury_sentences, entities):
    """
    Attempts to associate injury sentences with player names.
    entities: list of (name, type) tuples
    """
    players = [e[0] for e in entities if e[1] == "PERSON"]
    player_injuries = []

    for sent in injury_sentences:
        involved = [p for p in players if p in sent]
        player_injuries.append({
            "sentence": sent,
            "players": involved if involved else ["Unknown"]
        })

    return player_injuries
