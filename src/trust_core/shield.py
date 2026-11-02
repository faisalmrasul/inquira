"""Prohibited Practice Shield (EU AI Act Art. 5)."""

from __future__ import annotations

import re
from typing import Any, Dict

from src.config import MAX_SCAN_LEN


PROHIBITED_PATTERNS: Dict[str, list[str]] = {
    "social_scoring": [
        r"\bsocial\s*score\b", r"\bcredit\s*social\b", r"\brank\s+citizens\b",
    ],
    "manipulation": [
        r"\bsubliminal\b",
        r"\bmanipulat(e|ion)\s+(user|people|behaviou?r)\b",
        r"\bexploit\s+vulnerabilit",
    ],
    "emotion_inference_workplace_education": [
        r"\bemotion\s*(recognition|detection|inference)\b[\s\S]*\b(workplace|employee|student|classroom)\b",
        r"\bdetect\s+(employee|student|worker)\s+(emotion|mood|stress)\b",
    ],
    "biometric_categorisation_sensitive": [
        r"\bcategoris(e|ation)\b[\s\S]*\b(race|religion|sexual\s+orientation|political)\b",
    ],
    "real_time_biometric_public": [
        r"\breal[-\s]?time\s+(facial|biometric)\s+recognition\b[\s\S]*\bpublic\b",
    ],
    "predictive_policing_profiling": [
        r"\bpredict\s+crime\b[\s\S]*\bprofile\b",
        r"\brisk\s+score\b[\s\S]*\b(criminal|offen[cs]e)\b[\s\S]*\bprofil",
    ],
}


def scan_prohibited(text: str) -> Dict[str, Any]:
    """Scan text for Art. 5 prohibited-practice patterns."""
    if not isinstance(text, str):
        text = str(text)
    truncated = text[:MAX_SCAN_LEN]
    low = truncated.lower()
    hits = []
    for category, patterns in PROHIBITED_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, low, flags=re.IGNORECASE):
                hits.append({"category": category, "pattern": pat})
    return {
        "allowed": len(hits) == 0,
        "hits": hits,
        "article": "Art. 5 — Prohibited AI Practices",
        "truncated_input": len(text) > MAX_SCAN_LEN,
        "message": (
            "✅ No prohibited-practice pattern detected."
            if not hits else
            f"⛔ BLOCKED — {len(hits)} Art. 5 pattern(s) matched."
        ),
    }
