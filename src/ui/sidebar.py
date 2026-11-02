"""Sidebar renderer."""

from __future__ import annotations

import streamlit as st

from src.config import DISCLAIMER, FRAMEWORK_LABEL, EU_AI_ACT_REGULATION


def render_sidebar(workspace_options: list[str]) -> str:
    """Render sidebar and return the selected workspace."""
    with st.sidebar:
        st.markdown("## 🛡️ Inquira")
        st.caption("The Trust Layer · EU AI Act governance")
        st.divider()

        current = st.session_state.get("workspace", "💼 Professional")
        index = workspace_options.index(current) if current in workspace_options else 0
        selected = st.radio(
            "Workspace",
            options=workspace_options,
            index=index,
            key="workspace_selector",
        )
        st.session_state["workspace"] = selected

        st.divider()
        st.markdown("**Governance framework**")
        st.info(EU_AI_ACT_REGULATION)
        st.caption(DISCLAIMER)

        if st.session_state.get("approver_name"):
            st.success(
                f"Named approver on record: **{st.session_state['approver_name']}**"
            )

    return selected
