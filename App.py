import streamlit as st


st.set_page_config(
    page_title="GrantScopeAI",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 GrantScopeAI")

st.subheader(
    "Discover funded research projects related to your scientific concept"
)

st.write(
    """
    GrantScopeAI compares a research concept with funded NSF and CORDIS
    projects using an explainable similarity-search model.
    """
)

st.info(
    "GrantScopeAI identifies similar funded projects. "
    "It does not predict whether a proposal will receive funding."
)

st.success("Streamlit application loaded successfully.")