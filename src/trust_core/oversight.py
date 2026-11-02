"""Human oversight gate (EU AI Act Art. 14)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .registry import get_system


def human_oversight_gate(system_id: str, approver: Optional[str]) -> Dict[str, Any]:
    """Check whether human oversight is satisfied for a system."""
    reg = get_system(system_id)
    if not reg:
        return {"allowed": False, "reason": f"Unknown system '{system_id}'"}
    if not reg.human_oversight_required:
        return {"allowed": True}
    if not approver or not approver.strip():
        return {
            "allowed": False,
            "reason": (
                f"'{reg.name}' requires a named human approver before output "
                f"reaches end users (Art. 14(4)(d))."
            ),
        }
    return {"allowed": True, "approved_by": approver.strip()}
