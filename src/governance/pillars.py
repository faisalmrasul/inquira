"""RAI pillars and 'why flagged' anchors."""

from __future__ import annotations

from typing import Any, Dict, List


RAI_PILLARS: List[Dict[str, str]] = [
    {
        "key": "transparency",
        "title": "Transparency & AI Marking",
        "requirement": "Identifies AI content; avoids deception",
        "article": "Art. 13, Art. 50",
        "check_id": "transparency",
    },
    {
        "key": "bias",
        "title": "Bias & Non-Discrimination",
        "requirement": "Prevents unfair demographic / socioeconomic profiling",
        "article": "Art. 10",
        "check_id": "human_oversight",
    },
    {
        "key": "privacy",
        "title": "Data Privacy & Protection",
        "requirement": "GDPR / EU data compliance; scans for PII",
        "article": "Art. 10, GDPR Art. 5",
        "check_id": "data_minimisation",
    },
    {
        "key": "accuracy",
        "title": "Technical Accuracy & Factuality",
        "requirement": "Verifies grounding against uploaded files",
        "article": "Art. 15",
        "check_id": "determinism",
    },
]


WHY_FLAGGED_ANCHORS: Dict[str, str] = {
    "transparency": "Article 50 (Transparency obligations — AI-generated content must be marked)",
    "bias": "Article 10 (Data governance — training data must be examined for bias)",
    "privacy": "Article 10 & GDPR Article 5 (Data minimisation & purpose limitation)",
    "accuracy": "Article 15 (Accuracy, robustness & cybersecurity — outputs must be verifiable)",
    "prohibited_practices": "Article 5 (Prohibited AI practices — banned outright, no override)",
}


def build_why_flagged(verdict: Dict[str, Any]) -> str:
    """1–2 sentence explanation citing relevant EU AI Act articles."""
    failing = [c for c in verdict["checks"] if c["status"] in ("fail", "warn")]
    if not failing:
        return (
            "No flags raised. All four RAI pillars are satisfied under the "
            "EU AI Act (Reg. 2024/1689) — no remediation required."
        )

    reasons = []
    for c in failing:
        anchor = WHY_FLAGGED_ANCHORS.get(c["id"], "EU AI Act")
        reasons.append(f"{anchor}: {c['detail']}")

    lead = f"{len(failing)} RAI pillar(s) flagged. "
    return lead + " ".join(reasons[:2])
