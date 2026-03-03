import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from analyst.scorer import analyse_essay

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Essay Analyst",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS tweaks (minimal, targeted) ────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    h1 { letter-spacing: -0.5px; }
    .stMetric label { font-size: 0.78rem !important; color: #9BA3AF; }
    .stMetric [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 700; }
    div[data-testid="stProgress"] > div { border-radius: 6px; }
    .strength-box { background: #12281F; border-left: 3px solid #22C55E;
                    padding: 0.8rem 1rem; border-radius: 6px; margin-bottom: 0.5rem; }
    .weakness-box { background: #28161B; border-left: 3px solid #EF4444;
                    padding: 0.8rem 1rem; border-radius: 6px; margin-bottom: 0.5rem; }
    .roadmap-card { background: #1A1D27; border: 1px solid #2D3148;
                    border-radius: 8px; padding: 1rem 1.2rem; margin-bottom: 0.75rem; }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.title("📝 AI Essay Analyst")
st.caption("Research-grade academic feedback · RAG-assisted · Structured scoring")

with st.expander("ℹ️ How this works", expanded=False):
    st.markdown("""
    1. **Paste your essay** in the left panel and configure your academic context.
    2. The engine retrieves relevant academic references **(RAG)** to ground the analysis.
    3. A structured scorecard, strengths/weaknesses, and a prioritised revision plan are returned.
    4. Re-run after revisions to track improvement across the session.
    """)

st.divider()

# ── Layout: two main columns ──────────────────────────────────────────────────
left, right = st.columns([0.44, 0.56], gap="large")

# ═══════════════════════════════════════════════════════════
# LEFT PANEL — Input & Settings
# ═══════════════════════════════════════════════════════════
with left:
    st.subheader("1  ·  Essay Input")

    # Context metadata
    m1, m2 = st.columns(2)
    level      = m1.selectbox("Academic level",
                               ["Undergraduate", "Masters", "Doctoral / DBA"])
    discipline = m2.selectbox("Discipline",
                               ["General", "Business & Management",
                                "Computer Science", "Social Sciences",
                                "Education", "Health Sciences", "Other"])

    rubric = st.selectbox("Rubric profile",
                          ["Critical Essay", "Research Paper",
                           "Literature Review", "Research Proposal",
                           "Reflective Account", "Case Study Analysis"])

    essay_text = st.text_area(
        "Paste essay text",
        height=300,
        placeholder="Paste your full essay or the section you want analysed…",
    )

    uploaded = st.file_uploader("Or upload a plain-text file (.txt / .md)",
                                type=["txt", "md"])
    if uploaded and not essay_text:
        essay_text = uploaded.read().decode("utf-8")

    word_count = len(essay_text.split()) if essay_text else 0
    st.caption(f"Word count: **{word_count}** · Minimum required: 150 words")

    st.divider()
    st.subheader("2  ·  Analysis Settings")

    use_rag = st.toggle("Enable RAG (reference corpus retrieval)", value=True)
    max_refs = 7
    if use_rag:
        max_refs = st.slider("Max references to retrieve", 3, 15, 7)
        st.caption("References are drawn from the indexed academic corpus in `/data/corpus/`.")

    ready = word_count >= 150
    if not ready:
        st.warning("Please enter at least 150 words to enable analysis.")

    run = st.button("▶  Run analysis", type="primary",
                    disabled=not ready, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# RIGHT PANEL — Results
# ═══════════════════════════════════════════════════════════
with right:
    st.subheader("3  ·  Analysis Results")

    tabs = st.tabs(["📊 Overview", "📋 Detailed feedback",
                    "🔍 Sources & RAG", "🕑 Session history"])

    # ── BLANK STATE ──────────────────────────────────────────
    if "result" not in st.session_state and not run:
        with tabs[0]:
            st.info("No analysis yet. Complete the essay input on the left and click **Run analysis**.")
        with tabs[1]:
            st.empty()
        with tabs[2]:
            st.empty()
        with tabs[3]:
            st.empty()

    # ── RUN ANALYSIS ─────────────────────────────────────────
    if run and ready:
        with st.spinner("Analysing essay… retrieving references and scoring…"):
            result = analyse_essay(
                essay_text, level, discipline, rubric, use_rag, max_refs
            )
            st.session_state["result"] = result

            # Save to session history
            if "history" not in st.session_state:
                st.session_state["history"] = []
            st.session_state["history"].append({
                "run":     len(st.session_state["history"]) + 1,
                "overall": result["scores"]["overall"],
                "band":    result["band"],
                "level":   level,
                "rubric":  rubric,
            })

    # ── DISPLAY RESULTS ──────────────────────────────────────
    if "result" in st.session_state:
        r = st.session_state["result"]
        sc = r["scores"]

        # ── TAB 0: OVERVIEW ──────────────────────────────────
        with tabs[0]:

            # --- SCORECARD ---
            st.markdown("#### 📊 Scorecard")
            c0, c1, c2, c3, c4 = st.columns(5)

            def score_col(col, label, val):
                col.metric(label, f"{val}/100")
                col.progress(val / 100)

            score_col(c0, "🎯 Overall",        sc["overall"])
            score_col(c1, "🏗️ Structure",      sc["structure"])
            score_col(c2, "💡 Argument",        sc["argument_depth"])
            score_col(c3, "📚 Evidence",        sc["evidence_use"])
            score_col(c4, "🔗 Coherence",       sc["coherence"])

            band_colour = {"Distinction": "🟢", "Merit": "🔵",
                           "Pass": "🟡", "Developing": "🔴"}.get(r["band"], "⚪")
            st.markdown(f"**Grade band:** {band_colour} {r['band']}")

            # Radar chart
            cats = ["Structure", "Argument", "Evidence", "Coherence"]
            vals = [sc["structure"], sc["argument_depth"],
                    sc["evidence_use"], sc["coherence"]]
            fig = go.Figure(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill="toself", fillcolor="rgba(75,123
