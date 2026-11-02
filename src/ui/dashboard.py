"""Dashboard renderers — angles + RAI governance dashboard."""

from __future__ import annotations

import json
from typing import Any, Dict

import streamlit as st

from src.governance import (
    RAI_PILLARS,
    build_angles,
    build_compliance_certificate,
    classify_status,
)
from src.governance.pillars import build_why_flagged
from src.pipeline.evaluator import generate_autofix_output


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

    # Art. 5 shield result
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
