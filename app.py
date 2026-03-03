import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from analyst.scorer import analyse_essay

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
    div[data-testid="stProgress"] > div { border-radius: 6px; }
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

with st.expander("ℹ️ How this works", expanded=False):
    st.markdown("""
    1. **Paste your essay** in the left panel and configure your academic context.
    2. The engine retrieves relevant academic references **(RAG)** to ground the analysis.
    3. A structured scorecard, strengths/weaknesses, and a prioritised revision plan are returned.
    4. Re-run after revisions to track improvement across the session.
    """)

st.divider()

# ── Two-column layout ─────────────────────────────────────────────────────────
left, right = st.columns([0.44, 0.56], gap="large")

# ═════════════════════════════════════════════════════════════════════════════
# LEFT — Input & Settings
# ═════════════════════════════════════════════════════════════════════════════
with left:
    st.subheader("1  ·  Essay Input")

    m1, m2 = st.columns(2)
    level = m1.selectbox(
        "Academic level",
        ["Undergraduate", "Masters", "Doctoral / DBA"],
    )
    discipline = m2.selectbox(
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
        placeholder="Paste your full essay or the section you want analysed…",
    )

    uploaded = st.file_uploader(
        "Or upload a plain-text file (.txt / .md)",
        type=["txt", "md"],
    )
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
        st.caption(
            "References are drawn from the indexed academic corpus in `/data/corpus/`."
        )

    ready = word_count >= 150
    if not ready:
        st.warning("Please enter at least 150 words to enable analysis.")

    run = st.button(
        "▶  Run analysis",
        type="primary",
        disabled=not ready,
        use_container_width=True,
    )

# ═════════════════════════════════════════════════════════════════════════════
# RIGHT — Results
# ═════════════════════════════════════════════════════════════════════════════
with right:
    st.subheader("3  ·  Analysis Results")

    tabs = st.tabs(
        [
            "📊 Overview",
            "📋 Detailed feedback",
            "🔍 Sources & RAG",
            "🕑 Session history",
        ]
    )

    # Blank state
    if "result" not in st.session_state and not run:
        with tabs[0]:
            st.info(
                "No analysis yet. Complete the essay input on the left "
                "and click **Run analysis**."
            )
        with tabs[1]:
            st.empty()
        with tabs[2]:
            st.empty()
        with tabs[3]:
            st.empty()

    # Run analysis
    if run and ready:
        with st.spinner("Analysing essay… retrieving references and scoring…"):
            result = analyse_essay(
                essay_text, level, discipline, rubric, use_rag, max_refs
            )
            st.session_state["result"] = result

            if "history" not in st.session_state:
                st.session_state["history"] = []
            st.session_state["history"].append(
                {
                    "Run #":   len(st.session_state["history"]) + 1,
                    "Overall": result["scores"]["overall"],
                    "Band":    result["band"],
                    "Level":   level,
                    "Rubric":  rubric,
                }
            )

    # Display results
    if "result" in st.session_state:
        r  = st.session_state["result"]
        sc = r["scores"]

        # ── TAB 0: OVERVIEW ───────────────────────────────────────────────────
        with tabs[0]:

            st.markdown("#### 📊 Scorecard")
            c0, c1, c2, c3, c4 = st.columns(5)

            def score_col(col, label, val):
                col.metric(label, f"{val}/100")
                col.progress(int(val) / 100)

            score_col(c0, "🎯 Overall",   sc["overall"])
            score_col(c1, "🏗️ Structure", sc["structure"])
            score_col(c2, "💡 Argument",  sc["argument_depth"])
            score_col(c3, "📚 Evidence",  sc["evidence_use"])
            score_col(c4, "🔗 Coherence", sc["coherence"])

            band_icon = {
                "Distinction": "🟢",
                "Merit":       "🔵",
                "Pass":        "🟡",
                "Developing":  "🔴",
            }.get(r["band"], "⚪")
            st.markdown(f"**Grade band:** {band_icon} {r['band']}")

            # Radar chart
            cats      = ["Structure", "Argument", "Evidence", "Coherence"]
            vals      = [
                sc["structure"],
                sc["argument_depth"],
                sc["evidence_use"],
                sc["coherence"],
            ]
            r_vals    = vals + [vals[0]]
            r_theta   = cats + [cats[0]]

            fig = go.Figure(
                go.Scatterpolar(
                    r=r_vals,
                    theta=r_theta,
                    fill="toself",
                    fillcolor="rgba(75, 123, 229, 0.2)",
                    line=dict(color="rgba(75, 123, 229, 0.9)", width=2),
                )
            )
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=10),
                    ),
                    bgcolor="#1A1D27",
                ),
                paper_bgcolor="#0E1117",
                font=dict(color="#F0F2F6"),
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=False,
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True)

            st.divider()

            # Strengths & Weaknesses
            st.markdown("#### 💡 Strengths   &   ⚠️ Weaknesses")
            sw_l, sw_r = st.columns(2)

            with sw_l:
                st.caption("Strengths")
                for s in r.get("strengths", []):
                    st.markdown(
                        f'<div class="strength-box">'
                        f'<strong>{s["dimension"]}</strong><br>{s["point"]}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            with sw_r:
                st.caption("Weaknesses")
                for w in r.get("weaknesses", []):
                    st.markdown(
                        f'<div class="weakness-box">'
                        f'<strong>{w["dimension"]}</strong><br>{w["point"]}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            st.divider()

            # Revision Roadmap
            st.markdown("#### 🛠️ Revision Roadmap")
            for item in r.get("revision_roadmap", []):
                imp_icon = {
                    "High": "🔴", "Medium": "🟡", "Low": "🟢"
                }.get(item["impact"], "⚪")
                eff_icon = {
                    "Quick fix": "⚡", "Moderate": "🔧", "Deep revision": "🏗️"
                }.get(item["effort"], "")
                st.markdown(
                    f'<div class="roadmap-card">'
                    f'<strong>#{item["priority"]} · {item["dimension"]} — {item["title"]}</strong><br>'
                    f'{imp_icon} Impact: {item["impact"]} &nbsp;|&nbsp; '
                    f'{eff_icon} Effort: {item["effort"]}<br><br>'
                    f'{item["action"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.divider()

            # Confidence
            st.markdown("#### 🔬 Model Confidence")
            conf = float(r.get("confidence", 0.0))
            cf1, cf2 = st.columns([1, 2])
            with cf1:
                st.metric("Confidence score", f"{int(conf * 100)}%")
                st.progress(conf)
            with cf2:
                st.caption("What affects this score")
                st.markdown(r.get("confidence_notes", "No notes available."))
                sources = r.get("rag_sources", [])
                if sources:
                    st.caption(f"RAG: {len(sources)} reference(s) retrieved and used.")

        # ── TAB 1: DETAILED FEEDBACK ──────────────────────────────────────────
        with tabs[1]:
            st.markdown("#### 📋 Per-Dimension Detail")
            dim_map = {
                "structure":      "Structure",
                "argument_depth": "Argument Depth",
                "evidence_use":   "Evidence Use",
                "coherence":      "Coherence",
            }
            for dim_key, dim_label in dim_map.items():
                with st.expander(f"{dim_label}  —  {sc[dim_key]}/100"):
                    s_list = [
                        s for s in r.get("strengths", [])
                        if dim_label.lower() in s["dimension"].lower()
                    ]
                    w_list = [
                        w for w in r.get("weaknesses", [])
                        if dim_label.lower() in w["dimension"].lower()
                    ]
                    a_list = [
                        a for a in r.get("revision_roadmap", [])
                        if dim_label.lower() in a["dimension"].lower()
                    ]
                    if s_list:
                        st.markdown("**✅ Strengths**")
                        for s in s_list:
                            st.markdown(f"- {s['point']}")
                    if w_list:
                        st.markdown("**⚠️ Weaknesses**")
                        for w in w_list:
                            st.markdown(f"- {w['point']}")
                    if a_list:
                        st.markdown("**🛠️ Suggested actions**")
                        for a in a_list:
                            st.markdown(f"- {a['action']}")
                    if not s_list and not w_list and not a_list:
                        st.caption("No specific feedback mapped to this dimension.")

        # ── TAB 2: SOURCES & RAG ──────────────────────────────────────────────
        with tabs[2]:
            st.markdown("#### 🔍 Retrieved References")
            rag_sources = r.get("rag_sources", [])
            if rag_sources:
                st.dataframe(
                    pd.DataFrame(rag_sources),
                    use_container_width=True,
                )
            else:
                st.info(
                    "No RAG sources retrieved. "
                    "Enable RAG in Analysis Settings and re-run."
                )

        # ── TAB 3: SESSION HISTORY ────────────────────────────────────────────
        with tabs[3]:
            st.markdown("#### 🕑 Session Run History")
            history = st.session_state.get("history", [])
            if history:
                st.dataframe(
                    pd.DataFrame(history),
                    use_container_width=True,
                )
            else:
                st.info(
                    "No history yet. Run at least one analysis to start tracking."
                )
