"""Policy (legal) vs Governance (operational) angle builder."""

from __future__ import annotations

from typing import Any, Dict


POLICY_ANCHORS: Dict[str, Dict[str, str]] = {
    "human_oversight": {
        "article": "Art. 14 (Human oversight)",
        "requirement": "High-risk AI must be effectively overseen by natural persons.",
        "consequence": "Output may not reach end users without a named approver.",
    },
    "transparency": {
        "article": "Art. 13 & Art. 50 (Transparency)",
        "requirement": "Users must be informed they are interacting with an AI system.",
        "consequence": "Disclosure stamp is mandatory on every output.",
    },
    "data_minimisation": {
        "article": "Art. 10 & GDPR Art. 5 (Data governance)",
        "requirement": "Only necessary data processed; no retention beyond purpose.",
        "consequence": "Session-only processing; nothing retained for training.",
    },
    "determinism": {
        "article": "Art. 15 (Accuracy, robustness, cybersecurity)",
        "requirement": "Outputs must be reproducible for audit and contestation.",
        "consequence": "Numeric outputs are seeded; audit hash recorded.",
    },
    "prohibited_practices": {
        "article": "Art. 5 (Prohibited AI practices)",
        "requirement": "Certain uses are banned outright, regardless of safeguards.",
        "consequence": "Any match blocks execution — no human override.",
    },
}

GOVERNANCE_ANCHORS: Dict[str, Dict[str, str]] = {
    "human_oversight": {
        "control": "Named human approver gate",
        "evidence": "Approver identity captured in the hash-chained ledger.",
    },
    "transparency": {
        "control": "Disclosure injection at output boundary",
        "evidence": "Disclosure object attached to every allowed result.",
    },
    "data_minimisation": {
        "control": "Session-scoped processing, no persistence",
        "evidence": "No training writes; retention = request lifetime.",
    },
    "determinism": {
        "control": "Seeded execution + reproducibility hash",
        "evidence": "input_hash + prev_hash chain in compliance/events.jsonl.",
    },
    "prohibited_practices": {
        "control": "Pre-execution Art. 5 pattern shield",
        "evidence": "Scan result and matched patterns logged with the event.",
    },
}


def build_angles(verdict: Dict[str, Any]) -> Dict[str, Any]:
    checks = {c["id"]: c for c in verdict["checks"]}
    reg = verdict["system"]

    policy_rows = []
    for cid, anchor in POLICY_ANCHORS.items():
        chk = checks.get(cid)
        if not chk:
            continue
        policy_rows.append({
            "id": cid, "article": anchor["article"],
            "requirement": anchor["requirement"],
            "consequence": anchor["consequence"],
            "status": chk["status"], "detail": chk["detail"],
        })

    governance_rows = []
    for cid, anchor in GOVERNANCE_ANCHORS.items():
        chk = checks.get(cid)
        if not chk:
            continue
        governance_rows.append({
            "id": cid, "control": anchor["control"],
            "evidence": anchor["evidence"],
            "status": chk["status"], "detail": chk["detail"],
        })

    policy_failed = [r for r in policy_rows if r["status"] == "fail"]
    gov_failed = [r for r in governance_rows if r["status"] == "fail"]

    return {
        "system": reg,
        "policy": {
            "rows": policy_rows,
            "passed": len(policy_failed) == 0,
            "failed_count": len(policy_failed),
            "headline": (
                "Lawful under EU AI Act 2024/1689 as designed."
                if not policy_failed else
                f"Not lawful as submitted — {len(policy_failed)} Art. 5 / Art. 14 breach(es)."
            ),
        },
        "governance": {
            "rows": governance_rows,
            "passed": len(gov_failed) == 0,
            "failed_count": len(gov_failed),
            "headline": (
                "All organisational controls operated correctly."
                if not gov_failed else
                f"{len(gov_failed)} operational control(s) not satisfied."
            ),
        },
    }
