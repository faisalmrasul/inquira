"""AI disclosure texts (Art. 13, 50)."""

from __future__ import annotations

from typing import Any, Dict

from src.config import DISCLAIMER, utcnow
from .registry import AIRiskTier, get_system


DISCLOSURES = {
    AIRiskTier.HIGH: (
        "⚠️ AI-assisted. Output must be reviewed by a qualified human "
        "before reliance. You may contest this output (Art. 14, Art. 86)."
    ),
    AIRiskTier.LIMITED: "ℹ️ AI-generated content. Verify important information (Art. 50).",
    AIRiskTier.MINIMAL: "ℹ️ AI-powered suggestion (Art. 69).",
}


def build_disclosure(system_id: str) -> Dict[str, Any]:
    """Build the disclosure object attached to every allowed output."""
    reg = get_system(system_id)
    if not reg:
        raise ValueError(f"Unknown system '{system_id}'")
    return {
        "system_id": system_id,
        "system_name": reg.name,
        "risk_tier": reg.risk_tier.value,
        "annex_iii_category": reg.annex_iii_category,
        "disclosure_text": DISCLOSURES[reg.risk_tier],
        "human_oversight_required": reg.human_oversight_required,
        "generated_at": utcnow().isoformat(),
        "note": DISCLAIMER,
    }
