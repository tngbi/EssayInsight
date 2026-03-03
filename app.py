
import streamlit as st

st.set_page_config(page_title="AI Essay Analyst", layout="wide")

st.title("AI Essay Analyst")
st.caption("Structured academic feedback using RAG-assisted analysis.")

with st.expander("How this works"):
    st.markdown(
        "- Paste your essay on the left.\n"
        "- Configure level and rubric.\n"
        "- Run analysis to see structured feedback.\n"
    )

left_col, right_col = st.columns([0.45, 0.55])

with left_col:
    st.subheader("1. Essay input")

    level = st.selectbox(
        "Academic level",
        ["Undergraduate", "Masters", "Doctoral"],
    )

    discipline = st.selectbox(
        "Discipline",
        ["General", "Business", "Computer Science", "Social Science", "Other"],
    )

    rubric = st.selectbox(
        "Rubric profile",
        ["Critical Essay", "Research Paper", "Literature Review", "Proposal"],
    )

    essay_text = st.text_area(
        "Paste your essay",
        height=320,
        placeholder="Paste your essay here...",
    )

    st.divider()
    use_rag = st.toggle("Use reference corpus (RAG)", value=True)
    run_analysis = st.button(
        "Run analysis",
        type="primary",
        disabled=(len(essay_text.strip()) < 200),
    )

with right_col:
    st.subheader("Analysis results")

    tabs = st.tabs(["Overview", "Detailed feedback", "Sources & RAG", "History"])

    if not run_analysis:
        with tabs[0]:
            st.info("No analysis yet. Paste an essay and click Run analysis.")
    else:
        overall_score = 78
        struct_score = 80
        arg_score = 75
        evidence_score = 72
        coherence_score = 82
        confidence = 0.83

        with tabs[0]:
            st.markdown("### 📊 Scorecard")
            score_cols = st.columns(5)
            score_cols[0].metric("Overall", f"{overall_score}/100")
            score_cols[1].metric("Structure", f"{struct_score}/100")
            score_cols[2].metric("Argument depth", f"{arg_score}/100")
            score_cols[3].metric("Evidence use", f"{evidence_score}/100")
            score_cols[4].metric("Coherence", f"{coherence_score}/100")
            st.progress(overall_score / 100)

            st.divider()

            st.markdown("### 💡 Strengths & ⚠️ Weaknesses")
            sw_cols = st.columns(2)
            with sw_cols[0]:
                st.caption("Strengths")
                st.markdown("- **Structure**: Clear introduction and conclusion.")
            with sw_cols[1]:
                st.caption("Weaknesses")
                st.markdown("- **Argument depth**: Limited engagement with counterarguments.")

            st.divider()

            st.markdown("### 🛠️ Revision roadmap")
            st.markdown("**1. Add counterarguments**")
            st.caption("Impact: High · Effort: Moderate")
            st.write("Integrate at least two counterarguments in the main body.")

            st.divider()

            conf_cols = st.columns([1, 2])
            with conf_cols[0]:
                st.metric("Model confidence", f"{int(confidence * 100)}%")
                st.progress(confidence)
            with conf_cols[1]:
                st.caption("Confidence is based on essay completeness and consistency.")
