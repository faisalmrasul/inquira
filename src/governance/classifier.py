"""Status classifier — derives traffic-light status from verdict."""

from __future__ import annotations

from typing import Any, Dict


def classify_status(verdict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Derives the traffic-light status + confidence from the verdict.
      🟢 PASSED  / Minimal Risk  — allowed, no warnings
      🟡 WARNING / Limited Risk  — allowed, but >=1 warn check
      🔴 FAILED  / High Risk     — blocked, any fail check
    """
    statuses = [c["status"] for c in verdict["checks"]]
    n_pass = statuses.count("pass")
    n_warn = statuses.count("warn")
    n_fail = statuses.count("fail")
    total = len(statuses) or 1

    if n_fail > 0 or not verdict["allowed"]:
        level = "red"
        label = "🔴 FAILED / High Risk (Non-Compliant)"
        confidence = int(round(100 * (n_fail / total) + 60))
        confidence = min(confidence, 99)
    elif n_warn > 0:
        level = "yellow"
        label = "🟡 WARNING / Limited Risk (Requires Review)"
        confidence = int(round(100 * (n_pass / total) * 0.95))
    else:
        level = "green"
        label = "🟢 PASSED / Minimal Risk (Compliant)"
        confidence = int(round(100 * (n_pass / total) * 0.99))

    return {
        "level": level,
        "label": label,
        "confidence": max(confidence, 50),
        "counts": {"pass": n_pass, "warn": n_warn, "fail": n_fail},
    }
