"""Central configuration and constants."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Final


def utcnow() -> datetime:
    """Return timezone-aware UTC now."""
    return datetime.now(timezone.utc)


# --- Ledger -----------------------------------------------------------
DEFAULT_LEDGER_PATH: Final[str] = os.environ.get(
    "LEDGER_PATH", "compliance/events.jsonl"
)

# --- Limits -----------------------------------------------------------
MAX_SCAN_LEN: Final[int] = 50_000
MAX_ATTACHMENT_CHARS: Final[int] = 20_000
OUTPUT_SUMMARY_MAX: Final[int] = 300

# --- Framework --------------------------------------------------------
EU_AI_ACT_REGULATION: Final[str] = "Regulation (EU) 2024/1689 (EU AI Act)"
FRAMEWORK_LABEL: Final[str] = "EU AI Act (2024/2026)"
DISCLAIMER: Final[str] = (
    "Prototype — EU AI Act 2024/1689 used as a universal design standard. "
    "Not CE-marked. No legal compliance claim."
)

# --- Session state defaults ------------------------------------------
SESSION_DEFAULTS: Final[dict] = {
    "workspace": "💼 Professional",
    "approver_name": "",
    "last_verdict": None,
    "autofixed_output": None,
}
