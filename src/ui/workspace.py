"""Workspace renderer."""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from src.config import MAX_ATTACHMENT_CHARS
from src.pipeline.evaluator import evaluate_query, simulate_output
from src.trust_core import get_system
from src.governance import build_angles

from .dashboard import render_angles, render_rai_dashboard


WORKSPACES: Dict[str, Dict[str, str]] = {
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


def _read_uploaded_file(uploaded) -> str:
    """Extract text from an uploaded file (basic support)."""
    if uploaded is None:
        return ""
    try:
        raw = uploaded.read()
        name = uploaded.name.lower()
        if name.endswith(".pdf"):
            return "[PDF attached — text extraction would occur in production]"
        if name.endswith(".docx"):
            return "[DOCX attached — text extraction would occur in production]"
        return raw.decode("utf-8", errors="ignore")[:MAX_ATTACHMENT_CHARS]
    except Exception as exc:
        return f"[Could not read file: {exc}]"


def render_workspace(cfg: Dict[str, str]) -> None:
    system_id = cfg["system_id"]
    reg = get_system(system_id)
    if reg is None:
        st.error(f"Unknown system: {system_id}")
        return

    # Reset stale verdict when workspace changes
    if (
        st.session_state.get("last_verdict")
        and st.session_state["last_verdict"]["system"]["id"] != system_id
    ):
        st.session_state["last_verdict"] = None
        st.session_state["autofixed_output"] = None

    # ---- Hero + policy subtitle -----------------------------------
    st.markdown(
        f"""
    <div class="search-hero" style="padding-top:12px;">
      <h1 style="font-size:2rem;">{cfg['title']}</h1>
      <p>{cfg['subtitle']}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="text-align:center;">'
        '<span class="policy-badge">Governance Framework: EU AI Act (2024/2026)</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    # ---- Prompt bar -----------------------------------------------
    st.markdown('<div class="big-input">', unsafe_allow_html=True)
    prompt = st.text_area(
        "Ask anything",
        placeholder=cfg["example"],
        label_visibility="collapsed",
        key=f"prompt_{system_id}",
        height=90,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- File uploader + approver --------------------------------
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

    # ---- Action button -------------------------------------------
    st.write("")
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        run = st.button(
            "🛡️ Check Compliance",
            use_container_width=True,
            key=f"run_{system_id}",
            type="primary",
        )

    # ---- Execute -------------------------------------------------
    if run:
        if not prompt.strip() and not uploaded:
            st.warning("Enter a prompt or attach a file to validate.")
            return

        attachment_text = _read_uploaded_file(uploaded)
        verdict = evaluate_query(system_id, prompt, attachment_text, approver)
        st.session_state["last_verdict"] = verdict
        st.session_state["autofixed_output"] = None

    # ---- Render results ------------------------------------------
    verdict = st.session_state.get("last_verdict")
    if not verdict or verdict["system"]["id"] != system_id:
        return

    if verdict["allowed"]:
        st.markdown(
            '<div class="verdict-allow">'
            "<b>✅ Allowed.</b> "
            "<b>Policy:</b> lawful under EU AI Act as designed. "
            "<b>Governance:</b> oversight + transparency + ledger controls satisfied."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="verdict-block">'
            "<b>⛔ Blocked.</b> "
            "See the Policy and Governance angles below for the specific "
            "article and control that failed."
            "</div>",
            unsafe_allow_html=True,
        )

    render_rai_dashboard(verdict)

    st.markdown("---")
    angles = build_angles(verdict)
    render_angles(angles)

    if verdict["shield"]["hits"]:
        with st.expander("⛔ Art. 5 prohibited-practice hits", expanded=True):
            for hit in verdict["shield"]["hits"]:
                st.markdown(f"- **{hit['category']}** — pattern `{hit['pattern']}`")

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
            f"</span></div>",
            unsafe_allow_html=True,
        )

    entry = verdict["ledger"]
    st.caption(
        f"📒 Logged to hash-chained ledger · event hash "
        f"`{entry['hash'][:16]}…` · prev `{entry['prev_hash'][:16]}…`"
    )
