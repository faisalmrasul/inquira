"""Trust Core — risk tiers, registry, disclosure, oversight, shield."""

from .registry import (
    AIRiskTier,
    AISystemRegistration,
    AI_SYSTEM_REGISTRY,
    get_system,
)
from .shield import scan_prohibited, PROHIBITED_PATTERNS
from .oversight import human_oversight_gate
from .disclosure import DISCLOSURES, build_disclosure

__all__ = [
    "AIRiskTier",
    "AISystemRegistration",
    "AI_SYSTEM_REGISTRY",
    "get_system",
    "scan_prohibited",
    "PROHIBITED_PATTERNS",
    "human_oversight_gate",
    "DISCLOSURES",
    "build_disclosure",
]
