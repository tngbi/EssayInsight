import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from analyst.scorer import analyse_essay
from analyst.input_validation import validate_essay, count_words


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Essay Analyst",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
h1 { letter-spacing: -0.5px; }
.stMetric label { font-size: 0.78rem !important; color: #9BA3AF; }
.stMetric [data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700;
}
.strength-box {
    background: #12281F;
    border-left: 3px solid #22C55E;
    padding: 0.8rem 1rem;
    border-radius: 6px;
    margin-bottom: 0.5rem;
}
.weakness-box {
    background: #28161B;
    border-left: 3px solid #EF4444;
    padding: 0.8rem 1rem;
    border-radius: 6px;
    margin-bottom: 0.5rem;
}
.roadmap-card {
    background: #1A1D27;
    border: 1px solid #2D3148;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
}
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.title("📝 AI Essay Analyst")
st.caption("Research-grade academic feedback · RAG-assisted · Structured scoring")

st.divider()

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([0.44, 0.56], gap="large")

# ═════════════════════════════════════════════════════════════════════════════
# LEFT PANEL
# ═════════════════════════════════════════════════════════════════════════════
with left:

    st.subheader("1 · Essay Input")

    col1, col2 = st.columns(2)

    level = col1.selectbox(
        "Academic level",
        ["Undergraduate", "Masters", "Doctoral / DBA"]
    )

    discipline = col2.selectbox(
        "Discipline",
        [
            "General",
            "Business & Management",
            "Computer Science",
            "Social Sciences",
            "Education",
            "Health Sciences",
            "Other",
        ],
    )

    rubric = st.selectbox(
        "Rubric profile",
        [
            "Critical Essay",
            "Research Paper",
            "Literature Review",
            "Research Proposal",
            "Reflective Account",
            "Case Study Analysis",
        ],
    )

    essay_text = st.text_area(
        "Paste essay text",
        height=300,
        placeholder="Paste your essay here..."
    )

    uploaded = st.file_uploader(
        "Upload text file",
        type=["txt", "md"]
    )

    if uploaded and not essay_text:
        try:
            essay_text = uploaded.read().decode("utf-8")
        except:
            st.warning("Uploaded file is not valid UTF-8 text.")
            essay_text = ""

    word_count = count_words(essay_text)

    if essay_text:
        ok, msg = validate_essay(essay_text)
        if msg:
            st.warning(msg)

    st.caption(f"Word count: **{word_count}**")

    st.divider()

    st.subheader("2 · Analysis Settings")

    use_rag = st.toggle("Enable RAG retrieval", value=True)

    max_refs = 7
    if use_rag:
        max_refs = st.slider("Max references", 3, 15, 7)

    ready = word_count >= 150

    run = st.button(
        "▶ Run analysis",
        type="primary",
        disabled=not ready,
        use_container_width=True
    )

# ═════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL
# ═════════════════════════════════════════════════════════════════════════════
with right:

    st.subheader("3 · Analysis Results")

    tabs = st.tabs([
        "📊 Overview",
        "📋 Detailed feedback",
        "🔍 Sources",
        "🕑 Session history"
    ])

    # Run analysis
    if run and ready:

        with st.spinner("Analysing essay..."):

            result = analyse_essay(
                essay_text,
                level,
                discipline,
                rubric,
                use_rag,
                max_refs
            )

            st.session_state["result"] = result

            if "history" not in st.session_state:
                st.session_state["history"] = []

            scores = result.get("scores", {})

            st.session_state["history"].append({
                "Run #": len(st.session_state["history"]) + 1,
                "Overall": scores.get("overall"),
                "Band": result.get("band", "Unknown"),
                "Level": level,
                "Rubric": rubric,
            })

    # Display results
    if "result" in st.session_state:

        r = st.session_state.get("result", {})

        sc = r.get("scores", {
            "overall": 0,
            "structure": 0,
            "argument_depth": 0,
            "evidence_use": 0,
            "coherence": 0
        })

        # ── TAB 1 OVERVIEW ─────────────────────────────────────────────
        with tabs[0]:

            st.markdown("### Scorecard")

            cols = st.columns(5)

            def score_metric(col, label, val):
                val = val if isinstance(val, (int, float)) else 0
                col.metric(label, f"{val}/100")
                col.progress(val/100)

            score_metric(cols[0], "Overall", sc.get("overall", 0))
            score_metric(cols[1], "Structure", sc.get("structure", 0))
            score_metric(cols[2], "Argument", sc.get("argument_depth", 0))
            score_metric(cols[3], "Evidence", sc.get("evidence_use", 0))
            score_metric(cols[4], "Coherence", sc.get("coherence", 0))

            band = r.get("band", "Unknown")
            st.markdown(f"**Grade band:** {band}")

            # Radar chart
            categories = ["Structure", "Argument", "Evidence", "Coherence"]

            values = [
                sc.get("structure", 0),
                sc.get("argument_depth", 0),
                sc.get("evidence_use", 0),
                sc.get("coherence", 0)
            ]

            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself"
            ))

            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0,100])),
                showlegend=False,
                height=350
            )

            st.plotly_chart(fig, use_container_width=True)

        # ── TAB 2 FEEDBACK ─────────────────────────────────────────────
        with tabs[1]:

            st.markdown("### Detailed Feedback")

            strengths = r.get("strengths", [])
            weaknesses = r.get("weaknesses", [])

            if strengths:
                st.markdown("**Strengths**")
                for s in strengths:
                    st.markdown(
                        f"<div class='strength-box'>{s.get('point','')}</div>",
                        unsafe_allow_html=True
                    )

            if weaknesses:
                st.markdown("**Weaknesses**")
                for w in weaknesses:
                    st.markdown(
                        f"<div class='weakness-box'>{w.get('point','')}</div>",
                        unsafe_allow_html=True
                    )

        # ── TAB 3 SOURCES ──────────────────────────────────────────────
        with tabs[2]:

            sources = r.get("rag_sources", [])

            if sources:
                st.dataframe(pd.DataFrame(sources))
            else:
                st.info("No sources retrieved.")

        # ── TAB 4 HISTORY ──────────────────────────────────────────────
        with tabs[3]:

            history = st.session_state.get("history", [])

            if history:
                st.dataframe(pd.DataFrame(history))
            else:
                st.info("No session history yet.")
