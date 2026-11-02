"""CSS injection."""

from __future__ import annotations

import streamlit as st


_CSS = """
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
"""


def inject_css() -> None:
    """Inject Inquira CSS into the Streamlit app."""
    st.markdown(_CSS, unsafe_allow_html=True)
