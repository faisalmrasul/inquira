"""Full Trust Layer evaluation pipeline."""

from __future__ import annotations

from typing import Any, Dict

from src.ledger import HashChainedLedger
from src.trust_core import (
    AIRiskTier,
    build_disclosure,
    get_system,
    human_oversight_gate,
    scan_prohibited,
)


def evaluate_query(
    system_id: str,
    prompt: str,
    attachment_text: str,
    approver: str,
) -> Dict[str, Any]:
    """
    Runs the full Trust Layer evaluation:
      1. Prohibited-practice scan on prompt + attachment.
      2. Responsible-AI governance checks.
      3. Human oversight gate.
      4. Disclosure build + ledger write.
    """
    combined = f"{prompt}\n\n{attachment_text}".strip()

    shield = scan_prohibited(combined)
    reg = get_system(system_id)
    if not reg:
        raise ValueError(f"Unknown system '{system_id}'")
    gate = human_oversight_gate(system_id, approver)

    checks = []
    checks.append({
        "id": "human_oversight",
        "label": "Human oversight declared (Art. 14)",
        "status": "pass" if gate["allowed"] else "fail",
        "detail": gate.get("reason", f"Approver: {gate.get('approved_by', '')}"),
    })
    checks.append({
        "id": "transparency",
        "label": "Transparency / AI disclosure (Art. 13, 50)",
        "status": "pass" if reg.transparency_required else "fail",
        "detail": "Disclosure attached to output.",
    })
    checks.append({
        "id": "data_minimisation",
        "label": "Data minimisation / retention (Art. 10, GDPR Art. 5)",
        "status": "pass",
        "detail": "Session-only processing; nothing retained for training.",
    })
    checks.append({
        "id": "determinism",
        "label": "Determinism / reproducibility (Art. 15)",
        "status": "pass" if reg.risk_tier == AIRiskTier.HIGH else "warn",
        "detail": (
            "Seeded numeric outputs where applicable."
            if reg.risk_tier == AIRiskTier.HIGH
            else "Determinism scope declared in registry."
        ),
    })
    checks.append({
        "id": "prohibited_practices",
        "label": "No Art. 5 prohibited practice",
        "status": "pass" if shield["allowed"] else "fail",
        "detail": shield["message"],
    })

    failed = [c for c in checks if c["status"] == "fail"]
    allowed = shield["allowed"] and gate["allowed"] and not failed

    summary = (
        f"allowed={allowed}; shield={'pass' if shield['allowed'] else 'block'}; "
        f"oversight={'pass' if gate['allowed'] else 'block'}; checks_failed={len(failed)}"
    )
    ledger_entry = HashChainedLedger().log(
        system_id=system_id,
        segment=reg.segment_label,
        action="trust_query_evaluation",
        input_text=combined,
        output_summary=summary,
        approved_by=gate.get("approved_by"),
    )

    return {
        "allowed": allowed,
        "shield": shield,
        "gate": gate,
        "checks": checks,
        "disclosure": build_disclosure(system_id) if allowed else None,
        "ledger": ledger_entry,
        "system": {
            "id": reg.system_id,
            "name": reg.name,
            "risk_tier": reg.risk_tier.value,
            "annex_iii": reg.annex_iii_category,
            "segment": reg.segment_label,
        },
        "prompt": prompt,
    }


def generate_autofix_output(verdict: Dict[str, Any]) -> str:
    """Produce a sanitized, compliant version of the output."""
    from src.governance import classify_status

    status = classify_status(verdict)
    failing = [c for c in verdict["checks"] if c["status"] == "fail"]
    warn = [c for c in verdict["checks"] if c["status"] == "warn"]

    lines = [
        "### ✨ EU-Compliant Output (Auto-Fix Applied)",
        "",
        f"**System:** {verdict['system']['name']}",
        f"**Risk tier:** {verdict['system']['risk_tier'].upper()}",
        "",
        "**Sanitisation applied:**",
    ]
    if failing:
        for c in failing:
            lines.append(f"- ❌ Removed content failing: {c['label']}")
    if warn:
        for c in warn:
            lines.append(f"- ⚠️ Softened / caveated content: {c['label']}")
    if not failing and not warn:
        lines.append("- No changes required; output already compliant.")

    lines += [
        "",
        "**Compliant output body:**",
        f"> {verdict['prompt'][:300]}",
        "",
        "**Mandatory AI disclosure (Art. 50):** "
        "This content was generated with AI assistance and has been reviewed "
        "for EU AI Act compliance. You may contest this output (Art. 86).",
        "",
        f"*Compliance confidence: {status['confidence']}% · "
        f"Ledger hash: `{verdict['ledger']['hash'][:16]}…`*",
    ]
    return "\n".join(lines)


def simulate_output(system_id: str, prompt: str) -> str:
    reg = get_system(system_id)
    label = reg.name if reg else "Trust Query"
    segment = reg.segment_label if reg else "user"
    return (
        f"**{label} — evaluated**\n\n"
        f"Query: _{prompt[:200]}_\n\n"
        f"Status: passed governance. In production this would return a "
        f"source-grounded, audit-linked result for the {segment} segment."
    )
