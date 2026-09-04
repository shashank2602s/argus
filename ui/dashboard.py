import streamlit as st

from agents.evidence_graph import build_evidence_graph
from agents.investigator_loop import investigate_loop
from agents.state import InvestigationState
from models.investigation import Investigation


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

    # ============================================================
    # CLAIMS
    # ============================================================

    st.divider()
    st.header("📌 Claims")

    if state.claims:

        for claim in state.claims:

            with st.expander(
                f"{claim.status.value.upper()} — "
                f"{claim.confidence:.0%} confidence"
            ):

                st.write(
                    claim.statement
                )

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

                    st.write(
                        claim.evidence_excerpt
                    )

    else:

        st.info(
            "No claims were extracted."
        )

    # ============================================================
    # SOURCES
    # ============================================================

    st.divider()
    st.header("🌐 Sources")

    for source in state.sources:

        with st.expander(
            source.title or source.url
        ):

            st.write(
                f"**Domain:** {source.domain}"
            )

            st.write(
                f"**URL:** {source.url}"
            )

            if source.snippet:

                st.write(
                    source.snippet
                )

            if source.has_content:

                st.success(
                    "Content scraped successfully"
                )

            else:

                st.warning(
                    "Content was not scraped"
                )

    # ============================================================
    # EVIDENCE GRAPH
    # ============================================================

    st.divider()
    st.header("🕸️ Evidence Graph")

    st.caption(
        "Visual relationship between the investigation, "
        "extracted claims, and the sources supporting or "
        "challenging them."
    )

    investigation_view = Investigation(
        query=state.original_question,
        sources=state.sources,
        claims=state.claims,
    )

    graph = build_evidence_graph(
        investigation_view
    )

    # ------------------------------------------------------------
    # Graphviz configuration
    # ------------------------------------------------------------

    dot_lines = [
        "digraph EvidenceGraph {",

        # Layout
        "    rankdir=LR;",
        '    bgcolor="white";',
        '    graph [pad="0.5", nodesep="0.5", ranksep="1.0", '
        'bgcolor="white"];',

        # Default node styling
        '    node [fontname="Arial", '
        'fontsize=9, '
        'fontcolor="black", '
        'color="black", '
        'fillcolor="white", '
        'style="rounded,filled", '
        'margin="0.12,0.06"];',

        # Default edge styling
        '    edge [fontname="Arial", '
        'fontsize=8, '
        'fontcolor="black", '
        'color="gray40", '
        'arrowsize=0.7];',
    ]

    # ------------------------------------------------------------
    # Nodes
    # ------------------------------------------------------------

    for node in graph["nodes"]:

        node_id = (
            node["id"]
            .replace(":", "_")
            .replace("-", "_")
        )

        node_type = node["type"]

        # --------------------------------------------------------
        # Investigation node
        # --------------------------------------------------------

        if node_type == "investigation":

            question_text = node["label"]

            if len(question_text) > 55:

                question_text = (
                    question_text[:52]
                    + "..."
                )

            label = (
                "INVESTIGATION\\n"
                f"{question_text}"
            )

            label = label.replace(
                '"',
                '\\"',
            )

            dot_lines.append(
                f'    {node_id} '
                f'[label="{label}", '
                'shape=ellipse, '
                'fontcolor="black", '
                'color="black", '
                'fillcolor="white", '
                'fontsize=10, '
                'penwidth=2, '
                'style="filled"];'
            )

        # --------------------------------------------------------
        # Claim node
        # --------------------------------------------------------

        elif node_type == "claim":

            statement = node["label"]

            if len(statement) > 55:

                statement = (
                    statement[:52]
                    + "..."
                )

            status = node.get(
                "status",
                "unverified",
            ).upper()

            confidence = node.get(
                "confidence",
                0.0,
            )

            label = (
                "CLAIM\\n"
                f"{statement}\\n"
                f"{status} • {confidence:.0%}"
            )

            label = label.replace(
                '"',
                '\\"',
            )

            if node.get(
                "contested",
                False,
            ):

                dot_lines.append(
                    f'    {node_id} '
                    f'[label="{label}", '
                    'shape=box, '
                    'fontcolor="black", '
                    'color="black", '
                    'fillcolor="white", '
                    'penwidth=2, '
                    'style="rounded,filled"];'
                )

            else:

                dot_lines.append(
                    f'    {node_id} '
                    f'[label="{label}", '
                    'shape=box, '
                    'fontcolor="black", '
                    'color="black", '
                    'fillcolor="white", '
                    'penwidth=1.5, '
                    'style="rounded,filled"];'
                )

        # --------------------------------------------------------
        # Source node
        # --------------------------------------------------------

        elif node_type == "source":

            title = node["label"]

            if len(title) > 38:

                title = (
                    title[:35]
                    + "..."
                )

            domain = node.get(
                "domain",
                "",
            )

            if len(domain) > 30:

                domain = (
                    domain[:27]
                    + "..."
                )

            label = (
                "SOURCE\\n"
                f"{title}\\n"
                f"{domain}"
            )

            label = label.replace(
                '"',
                '\\"',
            )

            dot_lines.append(
                f'    {node_id} '
                f'[label="{label}", '
                'shape=note, '
                'fontcolor="black", '
                'color="black", '
                'fillcolor="white", '
                'penwidth=1.2, '
                'style="filled"];'
            )

    # ------------------------------------------------------------
    # Edges
    # ------------------------------------------------------------

    for edge in graph["edges"]:

        source = (
            edge["source"]
            .replace(":", "_")
            .replace("-", "_")
        )

        target = (
            edge["target"]
            .replace(":", "_")
            .replace("-", "_")
        )

        edge_type = edge["type"]

        # --------------------------------------------------------
        # Investigation → Claim
        # --------------------------------------------------------

        if edge_type == "investigates":

            dot_lines.append(
                f'    {source} -> {target} '
                '[color="gray50", '
                'penwidth=1.2, '
                'arrowsize=0.6, '
                'label=""];'
            )

        # --------------------------------------------------------
        # Claim → Supporting Source
        # --------------------------------------------------------

        elif edge_type == "supports":

            dot_lines.append(
                f'    {source} -> {target} '
                '[label="supports", '
                'color="green", '
                'fontcolor="green", '
                'penwidth=1.4, '
                'arrowsize=0.65];'
            )

        # --------------------------------------------------------
        # Claim → Contradicting Source
        # --------------------------------------------------------

        elif edge_type == "contradicts":

            dot_lines.append(
                f'    {source} -> {target} '
                '[label="contradicts", '
                'color="red", '
                'fontcolor="red", '
                'penwidth=1.6, '
                'style=dashed, '
                'arrowsize=0.65];'
            )

    # ------------------------------------------------------------
    # Legend
    # ------------------------------------------------------------

    dot_lines.extend(
        [
            "",
            "    legend [",
            "        shape=box,",
            '        label="EVIDENCE RELATIONSHIPS\\n\\n'
            'Green → Supporting evidence\\n'
            'Red dashed → Contradicting evidence",',
            '        fontcolor="black",',
            '        color="black",',
            '        fillcolor="white",',
            '        style="filled",',
            "        fontsize=8,",
            '        margin="0.15,0.10"',
            "    ];",
            "",
            "}",
        ]
    )

    # Render graph
    st.graphviz_chart(
        "\n".join(dot_lines),
        use_container_width=True,
    )

    # ============================================================
    # VERIFICATION TASKS
    # ============================================================

    st.divider()
    st.header("🔍 Verification Tasks")

    if state.verification_tasks:

        for task in state.verification_tasks:

            st.warning(
                task
            )

    else:

        st.success(
            "No additional verification tasks required."
        )

    # ============================================================
    # UNRESOLVED ISSUES
    # ============================================================

    if state.unresolved_questions:

        st.divider()
        st.header("⚠️ Unresolved Issues")

        for issue in state.unresolved_questions:

            st.error(
                issue
            )