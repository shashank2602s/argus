import streamlit as st

from agents.investigator_loop import investigate_loop
from agents.state import InvestigationState


st.set_page_config(
    page_title="ARGUS",
    page_icon="🔎",
    layout="wide",
)


st.title("🔎 ARGUS")
st.subheader("Autonomous Web Investigation & Evidence System")

st.markdown(
    "ARGUS searches the web, collects evidence, extracts claims, "
    "checks contradictions, and creates verification tasks."
)

st.divider()


question = st.text_input(
    "Investigation Question",
    placeholder="Example: What are the major cybersecurity trends in 2026?",
)


if st.button("🚀 Run Investigation", type="primary"):

    if not question.strip():
        st.warning("Please enter an investigation question.")
        st.stop()

    state = InvestigationState(
        original_question=question.strip()
    )

    state.objective = (
        "Investigate the question and identify claims "
        "supported by web evidence."
    )

    state.investigation_questions = [
        question.strip()
    ]

    state.search_queries = [
        question.strip(),
        f"{question.strip()} latest news",
        f"{question.strip()} official report",
    ]

    with st.spinner("ARGUS is investigating the web..."):
        state = investigate_loop(state)

    st.session_state["investigation"] = state


if "investigation" in st.session_state:

    state = st.session_state["investigation"]

    st.divider()
    st.header("📊 Investigation Results")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Sources Found",
        len(state.sources),
    )

    col2.metric(
        "Sources Scraped",
        state.usage_stats.get("sources_scraped", 0),
    )

    col3.metric(
        "Claims Extracted",
        len(state.claims),
    )

    col4.metric(
        "Contradictions",
        len(state.contradictions),
    )

    st.divider()

    # Claims
    st.header("📌 Claims")

    if state.claims:

        for claim in state.claims:

            with st.expander(
                f"{claim.status.value.upper()} — "
                f"{claim.confidence:.0%} confidence"
            ):

                st.write(claim.statement)

                st.write(
                    f"**Supporting sources:** "
                    f"{', '.join(claim.supporting_sources) or 'None'}"
                )

                st.write(
                    f"**Contradicting sources:** "
                    f"{', '.join(claim.contradicting_sources) or 'None'}"
                )

                if claim.evidence_excerpt:
                    st.caption("Evidence")
                    st.write(claim.evidence_excerpt)

    else:
        st.info("No claims were extracted.")

    # Sources
    st.divider()
    st.header("🌐 Sources")

    for source in state.sources:

        with st.expander(source.title or source.url):

            st.write(f"**Domain:** {source.domain}")
            st.write(f"**URL:** {source.url}")

            if source.snippet:
                st.write(source.snippet)

            if source.has_content:
                st.success("Content scraped successfully")
            else:
                st.warning("Content was not scraped")

    # Verification
    st.divider()
    st.header("🔍 Verification Tasks")

    if state.verification_tasks:

        for task in state.verification_tasks:
            st.warning(task)

    else:
        st.success("No additional verification tasks required.")

    # Unresolved issues
    if state.unresolved_questions:

        st.divider()
        st.header("⚠️ Unresolved Issues")

        for issue in state.unresolved_questions:
            st.error(issue)