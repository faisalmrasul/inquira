"""AI system registry — risk tiers and Annex III classifications."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from src.config import utcnow


class AIRiskTier(Enum):
    PROHIBITED = "prohibited"   # Art. 5
    HIGH       = "high"         # Art. 6 + Annex III
    LIMITED    = "limited"      # Art. 50
    MINIMAL    = "minimal"      # Art. 69


@dataclass
class AISystemRegistration:
    system_id: str
    name: str
    intended_purpose: str
    risk_tier: AIRiskTier
    human_oversight_required: bool
    transparency_required: bool
    annex_iii_category: Optional[str] = None
    segment_label: str = ""


AI_SYSTEM_REGISTRY: Dict[str, AISystemRegistration] = {
    "professional.trust_query": AISystemRegistration(
        system_id="professional.trust_query",
        name="Professional Trust Query Engine",
        intended_purpose="Research verification, audit-linked evaluation, portfolio analysis",
        risk_tier=AIRiskTier.HIGH,
        annex_iii_category="Annex III 5(b) — creditworthiness & financial decisions",
        human_oversight_required=True,
        transparency_required=True,
        segment_label="Professional",
    ),
    "business.trust_query": AISystemRegistration(
        system_id="business.trust_query",
        name="Business Owner Trust Query Engine",
        intended_purpose="Growth automation safety, predictive compliance, deterministic forecasting",
        risk_tier=AIRiskTier.HIGH,
        annex_iii_category="Annex III 5(b) — creditworthiness & financial decisions",
        human_oversight_required=True,
        transparency_required=True,
        segment_label="Business Owner",
    ),
    "student.trust_query": AISystemRegistration(
        system_id="student.trust_query",
        name="Student Assignment Trust Engine",
        intended_purpose="Assignment integrity checks, citation grounding, plagiarism-safe drafting",
        risk_tier=AIRiskTier.LIMITED,
        annex_iii_category=None,
        human_oversight_required=False,
        transparency_required=True,
        segment_label="Student",
    ),
    "teacher.trust_query": AISystemRegistration(
        system_id="teacher.trust_query",
        name="Teacher Lesson-Plan Compliance Engine",
        intended_purpose="Lesson plan compliance, curriculum alignment, assessment fairness review",
        risk_tier=AIRiskTier.HIGH,
        annex_iii_category="Annex III 3(b) — education & vocational training (assessment)",
        human_oversight_required=True,
        transparency_required=True,
        segment_label="Teacher",
    ),
}


def get_system(system_id: str) -> Optional[AISystemRegistration]:
    """Look up a registered AI system by id."""
    return AI_SYSTEM_REGISTRY.get(system_id)
