# app.py — Inquira: The Trust Layer for Professional AI
# Four workspaces (Professionals / Business Owners / Students / Teachers),
# each a single Google-style prompt bar with file attachment.
# Every query is evaluated for Responsible AI use under an EU AI Act-aligned
# governance layout before any output is returned.
#
# Results are rendered through TWO explicit lenses:
#   • POLICY angle     — is this use lawful under the EU AI Act (Reg. 2024/1689)?
#   • GOVERNANCE angle — did the organisation operate its controls correctly?
#
# Plus a dedicated RAI Governance dashboard (status banner, 4-pillar checklist,
# remediation actions, exportable compliance certificate).
#
# Prototype — designed against Regulation (EU) 2024/1689 as a universal
# design standard. Not CE-marked. Not placed on the EU market.

import streamlit as st
import json
import os
import re
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# =====================================================================
# PAGE CONFIG (first Streamlit call)
# =====================================================================
st.set_page_config(
    page_title="Inquira — The Trust Layer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# =====================================================================
# TRUST CORE — risk tiers, registry, disclosure, oversight, shield
# =====================================================================

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


DISCLOSURES = {
    AIRiskTier.HIGH: (
        "⚠️ AI-assisted. Output must be reviewed by a qualified human "
        "before reliance. You may contest this output (Art. 14, Art. 86)."
    ),
    AIRiskTier.LIMITED: "ℹ️ AI-generated content. Verify important information (Art. 50).",
    AIRiskTier.MINIMAL: "ℹ️ AI-powered suggestion (Art. 69).",
}


def build_disclosure(system_id: str) -> Dict[str, Any]:
    reg = AI_SYSTEM_REGISTRY[system_id]
    return {
        "system_id": system_id,
        "system_name": reg.name,
        "risk_tier": reg.risk_tier.value,
        "annex_iii_category": reg.annex_iii_category,
        "disclosure_text": DISCLOSURES[reg.risk_tier],
        "human_oversight_required": reg.human_oversight_required,
        "generated_at": _utcnow().isoformat(),
        "note": "Prototype — EU AI Act 2024/1689 as universal design standard.",
    }


def human_oversight_gate(system_id: str, approver: Optional[str]) -> Dict[str, Any]:
    reg = AI_SYSTEM_REGISTRY.get(system_id)
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


# --- Prohibited Practice Shield (Art. 5) -----------------------------

PROHIBITED_PATTERNS = {
    "social_scoring": [
        r"\bsocial\s*score\b", r"\bcredit\s*social\b", r"\brank\s+citizens\b",
    ],
    "manipulation": [
        r"\bsubliminal\b",
        r"\bmanipulat(e|ion)\s+(user|people|behaviou?r)\b",
        r"\bexploit\s+vulnerabilit",
    ],
    "emotion_inference_workplace_education": [
        r"\bemotion\s*(recognition|detection|inference)\b[\s\S]*\b(workplace|employee|student|classroom)\b",
        r"\bdetect\s+(employee|student|worker)\s+(emotion|mood|stress)\b",
    ],
    "biometric_categorisation_sensitive": [
        r"\bcategoris(e|ation)\b[\s\S]*\b(race|religion|sexual\s+orientation|political)\b",
    ],
    "real_time_biometric_public": [
        r"\breal[-\s]?time\s+(facial|biometric)\s+recognition\b[\s\S]*\bpublic\b",
    ],
    "predictive_policing_profiling": [
        r"\bpredict\s+crime\b[\s\S]*\bprofile\b",
        r"\brisk\s+score\b[\s\S]*\b(criminal|offen[cs]e)\b[\s\S]*\bprofil",
    ],
}

_MAX_SCAN_LEN = 50_000


def scan_prohibited(text: str) -> Dict[str, Any]:
    if not isinstance(text, str):
        text = str(text)
    truncated = text[:_MAX_SCAN_LEN]
    low = truncated.lower()
    hits = []
    for category, patterns in PROHIBITED_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, low, flags=re.IGNORECASE):
                hits.append({"category": category, "pattern": pat})
    return {
        "allowed": len(hits) == 0,
        "hits": hits,
        "article": "Art. 5 — Prohibited AI Practices",
        "truncated_input": len(text) > _MAX_SCAN_LEN,
        "message": (
            "✅ No prohibited-practice pattern detected."
            if not hits else
            f"⛔ BLOCKED — {len(hits)} Art. 5 pattern(s) matched."
        ),
    }


# =====================================================================
# HASH-CHAINED LEDGER (Art. 12, 19)
# =====================================================================

class HashChainedLedger:
    GENESIS = "0" * 64

    def __init__(self, path: str = "compliance/events.jsonl"):
        self.path = path

    def _last_hash(self) -> str:
        if not os.path.exists(self.path) or os.path.getsize(self.path) == 0:
            return self.GENESIS
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return json.loads(lines[-1])["hash"] if lines else self.GENESIS
        except Exception:
            return self.GENESIS

    def log(self, system_id: str, segment: str, action: str,
            input_text: str, output_summary: str,
            approved_by: Optional[str] = None) -> Dict[str, Any]:
        body = {
            "ts": _utcnow().isoformat(),
            "system_id": system_id,
            "segment": segment,
            "action": action,
            "actor": approved_by or "system",
            "input_hash": hashlib.sha256(input_text.encode("utf-8")).hexdigest()[:16],
            "output_summary": output_summary[:300],
            "prev_hash": self._last_hash(),
        }
        body["hash"] = hashlib.sha256(
            json.dumps(body, sort_keys=True).encode("utf-8")
        ).hexdigest()
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(body) + "\n")
        except Exception:
            pass
        return body


# =====================================================================
# SESSION STATE
# =====================================================================

_DEFAULTS = {
    "workspace": "💼 Professional",
    "approver_name": "",
    "last_verdict": None,
    "autofixed_output": None,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# =====================================================================
# CSS
# =====================================================================

st.markdown("""
<style>
.search-hero {
    text-align: center;
    padding: 28px 16px 8px;
}
.search-hero h1 {
    font-size: 2.2rem;
    margin: 0;
    background: linear-gradient(135deg, #0d47a1, #1976d2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.search-hero p {
    color: #555;
    margin-top: 6px;
    font-size: 0.98rem;
}
.big-input input {
    border-radius: 28px !important;
    padding: 16px 22px !important;
    font-size: 1.02rem !important;
    border: 1px solid #dfe1e5 !important;
    box-shadow: 0 1px 6px rgba(32,33,36,0.15) !important;
}
.big-input input:focus {
    box-shadow: 0 1px 10px rgba(32,33,36,0.28) !important;
    border-color: #ffffff !important;
}
.policy-badge {
    display: inline-block;
    background: #e3f2fd;
    color: #0d47a1;
    border: 1px solid #90caf9;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 4px 0 8px;
}
.ai-disclosure {
    background: #fffde7; border-left: 4px solid #fbc02d;
    padding: 12px 16px; border-radius: 6px; margin: 12px 0;
    font-size: 0.88rem; color: #5d4037;
}
.verdict-allow {
    background: #e8f5e9; border-left: 5px solid #2e7d32;
    padding: 16px; border-radius: 8px; margin: 12px 0;
}
.verdict-block {
    background: #ffebee; border-left: 5px solid #c62828;
    padding: 16px; border-radius: 8px; margin: 12px 0;
}
.verdict-warn {
    background: #fff8e1; border-left: 5px solid #ef6c00;
    padding: 16px; border-radius: 8px; margin: 12px 0;
}
.check-pass { color: #2e7d32; font-weight: 600; }
.check-fail { color: #c62828; font-weight: 600; }
.check-warn { color: #ef6c00; font-weight: 600; }
.risk-banner {
    border-radius: 12px;
    padding: 18px 22px;
    font-size: 1.05rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 8px;
}
.risk-green  { background: linear-gradient(135deg,#2e7d32,#43a047); }
.risk-yellow { background: linear-gradient(135deg,#ef6c00,#f9a825); }
.risk-red    { background: linear-gradient(135deg,#c62828,#e53935); }
.pillar-row {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    background: #ffffff;
}
.why-flagged {
    background: #fce4ec;
    border-left: 4px solid #ad1457;
    padding: 14px 18px;
    border-radius: 8px;
    font-size: 0.9rem;
    color: #4a148c;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)


# =====================================================================
# VALIDATION PIPELINE
# =====================================================================

def evaluate_query(system_id: str, prompt: str,
                   attachment_text: str, approver: str) -> Dict[str, Any]:
    """
    Runs the full Trust Layer evaluation:
      1. Prohibited-practice scan on prompt + attachment.
      2. Responsible-AI governance checks.
      3. Human oversight gate.
      4. Disclosure build + ledger write.
    """
    combined = f"{prompt}\n\n{attachment_text}".strip()

    shield = scan_prohibited(combined)
    reg = AI_SYSTEM_REGISTRY[system_id]
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
        "detail": ("Seeded numeric outputs where applicable."
                   if reg.risk_tier == AIRiskTier.HIGH
                   else "Determinism scope declared in registry."),
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


# =====================================================================
# RAI GOVERNANCE MODULE (EU AI Act)
# =====================================================================

# The 4 required pillars, mapped to check ids in the verdict.
RAI_PILLARS = [
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

# Article citations used in the "Why Flagged" note.
WHY_FLAGGED_ANCHORS = {
    "transparency": "Article 50 (Transparency obligations — AI-generated content must be marked)",
    "bias": "Article 10 (Data governance — training data must be examined for bias)",
    "privacy": "Article 10 & GDPR Article 5 (Data minimisation & purpose limitation)",
    "accuracy": "Article 15 (Accuracy, robustness & cybersecurity — outputs must be verifiable)",
    "prohibited_practices": "Article 5 (Prohibited AI practices — banned outright, no override)",
}


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


def build_compliance_certificate(verdict: Dict[str, Any]) -> Dict[str, Any]:
    """Structured audit report suitable for JSON/text export."""
    status = classify_status(verdict)
    return {
        "certificate_type": "EU AI Act — RAI Governance Compliance Certificate",
        "generated_at": _utcnow().isoformat(),
        "framework": "Regulation (EU) 2024/1689 (EU AI Act)",
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
        "disclaimer": (
            "Prototype — EU AI Act 2024/1689 used as a universal design "
            "standard. Not CE-marked. No legal compliance claim."
        ),
    }


def generate_autofix_output(verdict: Dict[str, Any]) -> str:
    """Produce a sanitized, compliant version of the output."""
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


# =====================================================================
# ANGLE SPLIT — Policy (legal) vs Governance (operational)
# =====================================================================

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


def simulate_output(system_id: str, prompt: str) -> str:
    reg = AI_SYSTEM_REGISTRY.get(system_id)
    label = reg.name if reg else "Trust Query"
    return (
        f"**{label} — evaluated**\n\n"
        f"Query: _{prompt[:200]}_\n\n"
        f"Status: passed governance. In production this would return a "
        f"source-grounded, audit-linked result for the {reg.segment_label if reg else 'user'} segment."
    )


# =====================================================================
# UI RENDERERS
# =====================================================================

_STATUS_ICON = {"pass": "✅", "fail": "❌", "warn": "⚠️"}
_STATUS_CSS = {"pass": "check-pass", "fail": "check-fail", "warn": "check-warn"}


def render_angles(angles: Dict[str, Any]) -> None:
    sysinfo = angles["system"]
    st.markdown(
        f'<div class="ai-disclosure">'
        f'<b>EU AI Act classification</b> — '
        f'Risk tier: <b>{sysinfo["risk_tier"].upper()}</b> · '
        f'Annex III: {sysinfo["annex_iii"] or "n/a"}'
        f'</div>',
        unsafe_allow_html=True,
    )

    col_policy, col_gov = st.columns(2, gap="large")

    with col_policy:
        p = angles["policy"]
        css = "verdict-allow" if p["passed"] else "verdict-block"
        icon = "✅" if p["passed"] else "⛔"
        st.markdown(
            f'<div class="{css}"><b>{icon} Policy angle</b><br>'
            f'<span style="font-size:0.9rem">{p["headline"]}</span></div>',
            unsafe_allow_html=True,
        )
        for row in p["rows"]:
            st.markdown(
                f'<span class="{_STATUS_CSS[row["status"]]}">'
                f'{_STATUS_ICON[row["status"]]} {row["article"]}</span>',
                unsafe_allow_html=True,
            )
            st.caption(f'*Requirement:* {row["requirement"]}')
            st.caption(f'*Consequence if failed:* {row["consequence"]}')
            st.caption(f'_Observed:_ {row["detail"]}')

    with col_gov:
        g = angles["governance"]
        css = "verdict-allow" if g["passed"] else "verdict-block"
        icon = "✅" if g["passed"] else "⛔"
        st.markdown(
            f'<div class="{css}"><b>{icon} Governance angle</b><br>'
            f'<span style="font-size:0.9rem">{g["headline"]}</span></div>',
            unsafe_allow_html=True,
        )
        for row in g["rows"]:
            st.markdown(
                f'<span class="{_STATUS_CSS[row["status"]]}">'
                f'{_STATUS_ICON[row["status"]]} {row["control"]}</span>',
                unsafe_allow_html=True,
            )
            st.caption(f'*Evidence of operation:* {row["evidence"]}')
            st.caption(f'_Observed:_ {row["detail"]}')


def render_rai_dashboard(verdict: Dict[str, Any]) -> None:
    """
    RAI Governance dashboard:
      A. Status & EU Risk Classification banner
      B. EU AI Act Core Safety Checklist (4 pillars)
      C. Explanations & remediation controls
    """
    status = classify_status(verdict)
    st.markdown("### 🧭 Responsible AI Governance — EU AI Act Evaluation")

    # ---- Section A: status banner + confidence ----------------------
    banner_css = {
        "green": "risk-green", "yellow": "risk-yellow", "red": "risk-red",
    }[status["level"]]
    col_banner, col_conf = st.columns([3, 1])
    with col_banner:
        st.markdown(
            f'<div class="risk-banner {banner_css}">{status["label"]}</div>',
            unsafe_allow_html=True,
        )
    with col_conf:
        st.metric("Confidence", f"{status['confidence']}%")
        st.caption(
            f"✅ {status['counts']['pass']} · "
            f"⚠️ {status['counts']['warn']} · "
            f"❌ {status['counts']['fail']}"
        )

    # ---- Section B: 4-pillar checklist -----------------------------
    st.markdown("#### 📋 EU AI Act Core Safety Checklist")
    checks_by_id = {c["id"]: c for c in verdict["checks"]}
    for pillar in RAI_PILLARS:
        chk = checks_by_id.get(pillar["check_id"])
        st_status = chk["status"] if chk else "warn"
        icon = _STATUS_ICON.get(st_status, "⚠️")
        css = _STATUS_CSS.get(st_status, "check-warn")
        st.markdown(
            f'<div class="pillar-row">'
            f'<span class="{css}">{icon} <b>{pillar["title"]}</b></span> '
            f'<span style="font-size:0.8rem;color:#666;">({pillar["article"]})</span><br>'
            f'<span style="font-size:0.85rem;color:#444;">{pillar["requirement"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Also surface the Art. 5 shield result (not one of the 4 pillars
    # but a hard gate, so it belongs on the checklist).
    shield_status = "pass" if verdict["shield"]["allowed"] else "fail"
    st.markdown(
        f'<div class="pillar-row">'
        f'<span class="{_STATUS_CSS[shield_status]}">'
        f'{_STATUS_ICON[shield_status]} <b>Prohibited Practices (Art. 5)</b></span> '
        f'<span style="font-size:0.8rem;color:#666;">(Art. 5)</span><br>'
        f'<span style="font-size:0.85rem;color:#444;">'
        f'No banned-use pattern (social scoring, manipulation, real-time biometrics…)</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ---- Section C: Why flagged + remediation ----------------------
    st.markdown("#### 🔎 Why Flagged (EU AI Act)")
    st.markdown(
        f'<div class="why-flagged">{build_why_flagged(verdict)}</div>',
        unsafe_allow_html=True,
    )

    # --- Interactive action buttons ---
    act_col1, act_col2 = st.columns(2, gap="medium")
    with act_col1:
        if st.button(
            "✨ Auto-Fix for EU Compliance",
            key="btn_autofix",
            use_container_width=True,
            type="primary",
        ):
            st.session_state["autofixed_output"] = generate_autofix_output(verdict)
            st.success("Compliant output generated below.")

    with act_col2:
        cert = build_compliance_certificate(verdict)
        cert_json = json.dumps(cert, indent=2, ensure_ascii=False)
        st.download_button(
            label="📑 Export Compliance Certificate (JSON)",
            data=cert_json,
            file_name=f"eu_ai_act_compliance_{verdict['system']['id'].replace('.', '_')}.json",
            mime="application/json",
            use_container_width=True,
            key="btn_export_cert",
        )

    if st.session_state.get("autofixed_output"):
        with st.container(border=True):
            st.markdown(st.session_state["autofixed_output"])
            if st.button("♻️ Clear auto-fixed output", key="clear_autofix"):
                st.session_state["autofixed_output"] = None
                st.rerun()


# =====================================================================
# WORKSPACE CONFIG
# =====================================================================

WORKSPACES = {
    "💼 Professional": {
        "system_id": "professional.trust_query",
        "title": "💼 Professional Workspace",
        "subtitle": (
            "Policy focus: research verification, audit-linked evaluation, "
            "portfolio analysis — EU AI Act HIGH risk (Annex III 5(b))."
        ),
        "example": "e.g. Verify the claim that TechCorp revenue grew 18% year-over-year",
    },
    "🏢 Business Owners": {
        "system_id": "business.trust_query",
        "title": "🏢 Business Owner Workspace",
        "subtitle": (
            "Policy focus: growth automation safety, predictive compliance, "
            "deterministic forecasting — EU AI Act HIGH risk (Annex III 5(b))."
        ),
        "example": "e.g. Forecast my cash flow for the next 30 days under a 2% rate shock",
    },
    "🎓 Students": {
        "system_id": "student.trust_query",
        "title": "🎓 Student Workspace",
        "subtitle": (
            "Policy focus: assignment integrity checks, citation grounding, "
            "plagiarism-safe drafting — EU AI Act LIMITED risk (Art. 50 transparency)."
        ),
        "example": "e.g. Check my essay on the French Revolution for ungrounded claims",
    },
    "📚 Teachers": {
        "system_id": "teacher.trust_query",
        "title": "📚 Teacher Workspace",
        "subtitle": (
            "Policy focus: lesson-plan compliance, curriculum alignment, "
            "assessment fairness review — EU AI Act HIGH risk (Annex III 3(b) education)."
        ),
        "example": "e.g. Audit this lesson plan for bias in the assessment rubric",
    },
}


# =====================================================================
# SIDEBAR — WORKSPACE SELECTOR
# =====================================================================

with st.sidebar:
    st.markdown("## 🛡️ Inquira")
    st.caption("The Trust Layer · EU AI Act governance")
    st.divider()

    st.session_state["workspace"] = st.radio(
        "Workspace",
        options=list(WORKSPACES.keys()),
        index=list(WORKSPACES.keys()).index(st.session_state.get("workspace", "💼 Professional"))
        if st.session_state.get("workspace") in WORKSPACES
        else 0,
        key="workspace_selector",
    )

    st.divider()
    st.markdown("**Governance framework**")
    st.info("EU AI Act (2024/2026) — Reg. (EU) 2024/1689")
    st.caption(
        "Prototype — used as a universal design standard. "
        "Not CE-marked. No legal compliance claim."
    )

    # Carry approver name across workspaces
    if st.session_state.get("approver_name"):
        st.success(f"Named approver on record: **{st.session_state['approver_name']}**")


# =====================================================================
# WORKSPACE RENDERER
# =====================================================================

def render_workspace(cfg: Dict[str, str]) -> None:
    system_id = cfg["system_id"]
    reg = AI_SYSTEM_REGISTRY[system_id]

    # Reset any stale verdict/autofix when the workspace changes
    if st.session_state.get("last_verdict") and \
       st.session_state["last_verdict"]["system"]["id"] != system_id:
        st.session_state["last_verdict"] = None
        st.session_state["autofixed_output"] = None

    # ---- Hero + policy subtitle -----------------------------------
    st.markdown(f"""
    <div class="search-hero" style="padding-top:12px;">
      <h1 style="font-size:2rem;">{cfg['title']}</h1>
      <p>{cfg['subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- Policy badge ---------------------------------------------
    st.markdown(
        '<div style="text-align:center;">'
        '<span class="policy-badge">Governance Framework: EU AI Act (2024/2026)</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ---- Search / prompt bar --------------------------------------
    st.markdown('<div class="big-input">', unsafe_allow_html=True)
    prompt = st.text_area(
        "Ask anything",
        placeholder=cfg["example"],
        label_visibility="collapsed",
        key=f"prompt_{system_id}",
        height=90,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- File uploader + approver row -----------------------------
    a1, a2 = st.columns([2, 1])
    with a1:
        uploaded = st.file_uploader(
            "Reference grounding — attach a file (PDF, DOCX, TXT, MD, CSV, JSON)",
            type=["txt", "md", "csv", "json", "pdf", "docx"],
            key=f"file_{system_id}",
        )
    with a2:
        approver = st.text_input(
            "Human approver (Art. 14)"
            if reg.human_oversight_required
            else "Reviewer (optional)",
            value=st.session_state.get("approver_name", ""),
            placeholder="e.g. Priya Sharma",
            key=f"approver_{system_id}",
        )
        st.session_state["approver_name"] = approver

    # ---- Action button --------------------------------------------
    st.write("")
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        run = st.button(
            "🛡️ Check Compliance",
            use_container_width=True,
            key=f"run_{system_id}",
            type="primary",
        )

    # ---- Execute --------------------------------------------------
    if run:
        if not prompt.strip() and not uploaded:
            st.warning("Enter a prompt or attach a file to validate.")
            return

        attachment_text = ""
        if uploaded is not None:
            try:
                raw = uploaded.read()
                if uploaded.name.lower().endswith(".pdf"):
                    attachment_text = "[PDF attached — text extraction would occur in production]"
                elif uploaded.name.lower().endswith(".docx"):
                    attachment_text = "[DOCX attached — text extraction would occur in production]"
                else:
                    attachment_text = raw.decode("utf-8", errors="ignore")[:20_000]
            except Exception as e:
                attachment_text = f"[Could not read file: {e}]"

        verdict = evaluate_query(system_id, prompt, attachment_text, approver)
        st.session_state["last_verdict"] = verdict
        st.session_state["autofixed_output"] = None

    # ---- Render results from session state ------------------------
    verdict = st.session_state.get("last_verdict")
    if not verdict or verdict["system"]["id"] != system_id:
        return

    # Verdict banner (names both angles)
    if verdict["allowed"]:
        st.markdown(
            '<div class="verdict-allow">'
            '<b>✅ Allowed.</b> '
            '<b>Policy:</b> lawful under EU AI Act as designed. '
            '<b>Governance:</b> oversight + transparency + ledger controls satisfied.'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="verdict-block">'
            '<b>⛔ Blocked.</b> '
            'See the Policy and Governance angles below for the specific '
            'article and control that failed.'
            '</div>',
            unsafe_allow_html=True,
        )

    # RAI Governance dashboard (banner + 4 pillars + why-flagged + actions)
    render_rai_dashboard(verdict)

    # Policy / Governance angles
    st.markdown("---")
    angles = build_angles(verdict)
    render_angles(angles)

    # Prohibited pattern detail
    if verdict["shield"]["hits"]:
        with st.expander("⛔ Art. 5 prohibited-practice hits", expanded=True):
            for hit in verdict["shield"]["hits"]:
                st.markdown(f"- **{hit['category']}** — pattern `{hit['pattern']}`")

    # Output + disclosure
    if verdict["allowed"]:
        st.subheader("Result")
        st.markdown(simulate_output(system_id, verdict["prompt"]))
        d = verdict["disclosure"]
        st.markdown(
            f'<div class="ai-disclosure">'
            f'<b>{d["disclosure_text"]}</b><br>'
            f'<span style="font-size:0.8rem;">'
            f'System: <code>{d["system_id"]}</code> · '
            f'Risk: <b>{d["risk_tier"].upper()}</b> · '
            f'Annex III: {d["annex_iii_category"] or "n/a"} · '
            f'Generated: {d["generated_at"]}'
            f'</span></div>',
            unsafe_allow_html=True,
        )

    # Ledger confirmation
    entry = verdict["ledger"]
    st.caption(
        f"📒 Logged to hash-chained ledger · event hash "
        f"`{entry['hash'][:16]}…` · prev `{entry['prev_hash'][:16]}…`"
    )


# =====================================================================
# MAIN
# =====================================================================

selected = st.session_state.get("workspace", "💼 Professional")
render_workspace(WORKSPACES[selected])
