"""Compliance certificate builder."""

from __future__ import annotations

from typing import Any, Dict

from src.config import DISCLAIMER, EU_AI_ACT_REGULATION, utcnow
from .classifier import classify_status
from .pillars import RAI_PILLARS, build_why_flagged


def build_compliance_certificate(verdict: Dict[str, Any]) -> Dict[str, Any]:
    """Structured audit report suitable for JSON/text export."""
    status = classify_status(verdict)
    return {
        "certificate_type": "EU AI Act — RAI Governance Compliance Certificate",
        "generated_at": utcnow().isoformat(),
        "framework": EU_AI_ACT_REGULATION,
        "platform": "Inquira",
        "system": verdict["system"],
        "status": {
            "label": status["label"],
            "level": status["level"],
            "confidence": f"{status['confidence']}%",
        },
        "pillars": [
            {
                "title": p["title"],
                "requirement": p["requirement"],
                "article": p["article"],
                "status": next(
                    (c["status"] for c in verdict["checks"] if c["id"] == p["check_id"]),
                    "n/a",
                ),
            }
            for p in RAI_PILLARS
        ],
        "why_flagged": build_why_flagged(verdict),
        "checks": verdict["checks"],
        "ledger": {
            "hash": verdict["ledger"]["hash"],
            "prev_hash": verdict["ledger"]["prev_hash"],
            "ts": verdict["ledger"]["ts"],
        },
        "disclaimer": DISCLAIMER,
    }
