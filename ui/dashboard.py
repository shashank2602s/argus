import traceback

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

st.divider()


# ============================================================
# LANDING STATE — INTRO, PIPELINE PREVIEW, EXAMPLES
# ============================================================
# Purely presentational additions below. No pipeline, Anakin,
# claim/graph, or verification logic is touched.

st.markdown(
    """
    <style>
    .argus-intro-card {
        background-color: #f8f9fb;
        border: 1px solid #e3e6eb;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.1rem;
        font-size: 0.95rem;
        line-height: 1.55;
        color: #31333f;
    }
    .argus-pipeline {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.4rem;
        flex-wrap: wrap;
        margin: 0.25rem 0 1.4rem 0;
    }
    .argus-pipeline-step {
        background-color: #f0f2f6;
        border: 1px solid #d0d4da;
        border-radius: 6px;
        padding: 0.35rem 0.9rem;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        color: #31333f;
        white-space: nowrap;
    }
    .argus-pipeline-arrow {
        color: #9aa0ab;
        font-size: 0.95rem;
    }
    .argus-examples-label {
        font-size: 0.82rem;
        color: #6b7280;
        margin-top: 0.6rem;
        margin-bottom: 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="argus-intro-card">
    ARGUS investigates web questions using live evidence, extracts claims,
    checks supporting and contradicting sources, and produces traceable
    evidence for every conclusion it reaches.
    </div>
    """,
    unsafe_allow_html=True,
)

_pipeline_steps = ["QUESTION", "SEARCH", "SOURCES", "CLAIMS", "VERIFY"]
_pipeline_html = ['<div class="argus-pipeline">']
for _i, _step in enumerate(_pipeline_steps):
    _pipeline_html.append(f'<div class="argus-pipeline-step">{_step}</div>')
    if _i < len(_pipeline_steps) - 1:
        _pipeline_html.append('<div class="argus-pipeline-arrow">→</div>')
_pipeline_html.append("</div>")

st.markdown("".join(_pipeline_html), unsafe_allow_html=True)


# Example questions the user can click to populate the input.
# Clicking only fills the text field — it never triggers an
# investigation or calls Anakin.
EXAMPLE_QUESTIONS = [
    "What are the major cybersecurity trends in 2026?",
    "Is there evidence of a recent supply-chain attack on open-source packages?",
    "What are the known risks of AI-generated phishing campaigns?",
    "Are there credible reports of a new ransomware group targeting healthcare?",
]

# A pending-value handoff is used so the text_input's value can be
# updated *before* the widget is instantiated on the next rerun,
# which avoids Streamlit's restriction on mutating a widget's own
# session_state key after it has been created.
if "argus_pending_question" in st.session_state:
    st.session_state["argus_question"] = st.session_state.pop(
        "argus_pending_question"
    )

question = st.text_input(
    "Investigation Question",
    key="argus_question",
    placeholder="Example: What are the major cybersecurity trends in 2026?",
)

st.markdown(
    '<div class="argus-examples-label">Try an example:</div>',
    unsafe_allow_html=True,
)

_example_cols = st.columns(len(EXAMPLE_QUESTIONS))
for _col, _example in zip(_example_cols, EXAMPLE_QUESTIONS):
    with _col:
        if st.button(_example, key=f"example_{_example}", use_container_width=True):
            st.session_state["argus_pending_question"] = _example
            st.rerun()

st.divider()


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

    # The try/except below only catches and displays unexpected
    # runtime errors from the existing investigate_loop call. It
    # does not change, wrap, retry, or alter pipeline behavior in
    # any way — on success, execution proceeds exactly as before.
    try:

        with st.spinner("ARGUS is investigating the web..."):
            state = investigate_loop(state)

        st.session_state["investigation"] = state

    except Exception as exc:

        st.error(
            "ARGUS hit an unexpected error while investigating this "
            "question, and the run did not complete. The pipeline "
            "itself hasn't changed — this is just a runtime error "
            "being surfaced clearly instead of leaving the page in "
            "a broken state."
        )

        with st.expander("Technical details"):
            st.code(
                f"{type(exc).__name__}: {exc}\n\n"
                f"{traceback.format_exc()}"
            )


if "investigation" in st.session_state:

    state = st.session_state["investigation"]

    st.divider()
    st.header("📊 Investigation Results")

    # ------------------------------------------------------------
    # Overview metric cards (presentation only — values below are
    # computed exactly as before; no pipeline logic is touched).
    # ------------------------------------------------------------

    st.markdown(
        """
        <style>
        .argus-metric-card {
            background-color: #f8f9fb;
            border: 1px solid #e3e6eb;
            border-radius: 8px;
            padding: 0.9rem 1rem 1rem 1rem;
            text-align: left;
        }
        .argus-metric-label {
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            color: #6b7280;
            text-transform: uppercase;
        }
        .argus-metric-value {
            font-size: 1.9rem;
            font-weight: 700;
            color: #1f2430;
            margin: 0.15rem 0 0.2rem 0;
            line-height: 1.1;
        }
        .argus-metric-desc {
            font-size: 0.78rem;
            color: #8a8f99;
        }
        .argus-metric-card--alert {
            background-color: #fdf2f2;
            border: 1px solid #f3b4b4;
        }
        .argus-metric-card--alert .argus-metric-label {
            color: #b3261e;
        }
        .argus-metric-card--alert .argus-metric-value {
            color: #b3261e;
        }
        .argus-metric-card--alert .argus-metric-desc {
            color: #b3261e;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    sources_found = len(state.sources)
    sources_scraped = state.usage_stats.get("sources_scraped", 0)
    claims_extracted = len(state.claims)
    contradictions_count = len(state.contradictions)

    def _argus_metric_card(label, value, description, alert=False):
        card_class = (
            "argus-metric-card argus-metric-card--alert"
            if alert
            else "argus-metric-card"
        )
        return (
            f'<div class="{card_class}">'
            f'<div class="argus-metric-label">{label}</div>'
            f'<div class="argus-metric-value">{value}</div>'
            f'<div class="argus-metric-desc">{description}</div>'
            f'</div>'
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            _argus_metric_card(
                "Sources Found",
                sources_found,
                "web sources discovered",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            _argus_metric_card(
                "Sources Scraped",
                sources_scraped,
                "sources actually inspected",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            _argus_metric_card(
                "Claims Extracted",
                claims_extracted,
                "evidence-backed claims identified",
            ),
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            _argus_metric_card(
                "Contradictions",
                contradictions_count,
                "conflicting evidence detected",
                alert=contradictions_count > 0,
            ),
            unsafe_allow_html=True,
        )

    # ------------------------------------------------------------
    # How ARGUS Works (explanatory only — displays the existing
    # pipeline stages as static text; it does not execute, re-run,
    # or modify any pipeline step).
    # ------------------------------------------------------------

    with st.expander("🔬 How ARGUS Works"):

        st.caption(
            "A high-level view of the investigation pipeline behind "
            "these results. This is explanatory only."
        )

        _how_it_works_steps = [
            "QUESTION",
            "SEARCH",
            "SOURCE SELECTION",
            "SCRAPING",
            "CLAIM EXTRACTION",
            "CONTRADICTION DETECTION",
            "CROSS-SOURCE MATCHING",
            "VERIFICATION",
        ]
        _how_it_works_html = ['<div class="argus-pipeline">']
        for _i, _step in enumerate(_how_it_works_steps):
            _how_it_works_html.append(
                f'<div class="argus-pipeline-step">{_step}</div>'
            )
            if _i < len(_how_it_works_steps) - 1:
                _how_it_works_html.append(
                    '<div class="argus-pipeline-arrow">→</div>'
                )
        _how_it_works_html.append("</div>")

        st.markdown("".join(_how_it_works_html), unsafe_allow_html=True)

    # ============================================================
    # CLAIMS
    # ============================================================

    st.divider()
    st.header("📌 Claims")

    # ------------------------------------------------------------
    # Claim card styling (presentation only — claim.status,
    # claim.confidence, claim.supporting_sources,
    # claim.contradicting_sources, and claim.evidence_excerpt are
    # read as-is; nothing here recalculates or alters them).
    # ------------------------------------------------------------

    st.markdown(
        """
        <style>
        .argus-claim-statement {
            font-size: 1.02rem;
            font-weight: 600;
            color: #1f2430;
            line-height: 1.45;
            margin-bottom: 0.7rem;
            word-break: break-word;
            overflow-wrap: anywhere;
        }
        .argus-status-badge {
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            padding: 0.18rem 0.6rem;
            border-radius: 999px;
            text-transform: uppercase;
        }
        .argus-confidence-row {
            margin: 0.7rem 0 0.9rem 0;
        }
        .argus-confidence-label {
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            color: #6b7280;
            text-transform: uppercase;
            margin-bottom: 0.2rem;
        }
        .argus-evidence-block {
            display: block;
            border-radius: 8px;
            padding: 0.7rem 0.9rem;
            margin-bottom: 0.6rem;
        }
        .argus-evidence-block--supporting {
            background-color: #f1f9f3;
            border: 1px solid #bfe3c8;
        }
        .argus-evidence-block--contradicting {
            background-color: #fdf2f2;
            border: 1px solid #f3b4b4;
        }
        .argus-evidence-block-title {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }
        .argus-evidence-block--supporting .argus-evidence-block-title {
            color: #1f7a3d;
        }
        .argus-evidence-block--contradicting .argus-evidence-block-title {
            color: #b3261e;
        }
        .argus-source-chip {
            display: inline-block;
            font-size: 0.75rem;
            font-family: monospace;
            background-color: #ffffff;
            border: 1px solid #d0d4da;
            border-radius: 5px;
            padding: 0.1rem 0.45rem;
            margin: 0.1rem 0.3rem 0.1rem 0;
        }
        .argus-evidence-none {
            font-size: 0.8rem;
            color: #8a8f99;
            font-style: italic;
        }
        .argus-empty-state {
            background-color: #f8f9fb;
            border: 1px solid #e3e6eb;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.9rem;
            color: #6b7280;
        }
        .argus-excerpt-box {
            background-color: #f8f9fb;
            border-left: 3px solid #9aa0ab;
            border-radius: 4px;
            padding: 0.65rem 0.9rem;
            margin-top: 0.3rem;
            font-size: 0.88rem;
            font-style: italic;
            color: #31333f;
            line-height: 1.5;
            word-break: break-word;
            overflow-wrap: anywhere;
        }
        .argus-excerpt-label {
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            color: #6b7280;
            text-transform: uppercase;
            margin-top: 0.6rem;
            margin-bottom: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def _argus_status_colors(status_text):
        status_lower = status_text.lower()
        if "contradict" in status_lower:
            return "#b3261e", "#fdf2f2", "#f3b4b4"
        if "unverified" in status_lower or "pending" in status_lower:
            return "#8a6d1d", "#fbf6e8", "#eadfb0"
        if "verif" in status_lower:
            return "#1f7a3d", "#f1f9f3", "#bfe3c8"
        return "#374151", "#f0f2f6", "#d0d4da"

    def _argus_source_chips(source_ids):
        if not source_ids:
            return '<span class="argus-evidence-none">None identified</span>'
        return "".join(
            f'<span class="argus-source-chip">{sid}</span>' for sid in source_ids
        )

    if state.claims:

        for claim in state.claims:

            status_text = claim.status.value.upper()
            text_color, bg_color, border_color = _argus_status_colors(status_text)

            claim_preview = claim.statement
            if len(claim_preview) > 70:
                claim_preview = claim_preview[:67] + "..."

            expander_label = (
                f"{status_text} — {claim.confidence:.0%} confidence — "
                f"{claim_preview}"
            )

            with st.expander(expander_label):

                # --- Claim statement, shown prominently ---
                st.markdown(
                    f'<div class="argus-claim-statement">{claim.statement}</div>',
                    unsafe_allow_html=True,
                )

                # --- Status badge ---
                st.markdown(
                    f'<span class="argus-status-badge" '
                    f'style="color:{text_color}; background-color:{bg_color}; '
                    f'border:1px solid {border_color};">{status_text}</span>',
                    unsafe_allow_html=True,
                )

                # --- Confidence, shown as percentage + bar (value unchanged) ---
                st.markdown(
                    '<div class="argus-confidence-row">'
                    '<div class="argus-confidence-label">'
                    f"Confidence — {claim.confidence:.0%}"
                    "</div></div>",
                    unsafe_allow_html=True,
                )
                st.progress(min(max(claim.confidence, 0.0), 1.0))

                # --- Supporting sources ---
                st.markdown(
                    '<div class="argus-evidence-block argus-evidence-block--supporting">'
                    '<div class="argus-evidence-block-title">'
                    f"Supporting sources ({len(claim.supporting_sources)})"
                    "</div>"
                    f"{_argus_source_chips(claim.supporting_sources)}"
                    "</div>",
                    unsafe_allow_html=True,
                )

                # --- Contradicting sources ---
                st.markdown(
                    '<div class="argus-evidence-block argus-evidence-block--contradicting">'
                    '<div class="argus-evidence-block-title">'
                    f"Contradicting sources ({len(claim.contradicting_sources)})"
                    "</div>"
                    f"{_argus_source_chips(claim.contradicting_sources)}"
                    "</div>",
                    unsafe_allow_html=True,
                )

                # --- Evidence excerpt, visually separated from the claim ---
                if claim.evidence_excerpt:

                    st.markdown(
                        '<div class="argus-excerpt-label">Evidence excerpt</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="argus-excerpt-box">{claim.evidence_excerpt}</div>',
                        unsafe_allow_html=True,
                    )

    else:

        st.markdown(
            '<div class="argus-empty-state">No claims were extracted.</div>',
            unsafe_allow_html=True,
        )

    # ============================================================
    # SOURCES
    # ============================================================

    st.divider()
    st.header("🌐 Sources")

    # ------------------------------------------------------------
    # Source card styling (presentation only — source.title,
    # source.domain, source.url, source.snippet, and
    # source.has_content are read as-is; nothing here alters the
    # Source objects or investigation state).
    # ------------------------------------------------------------

    st.markdown(
        """
        <style>
        .argus-source-title {
            font-size: 1.0rem;
            font-weight: 600;
            color: #1f2430;
            margin-bottom: 0.4rem;
            word-break: break-word;
        }
        .argus-source-meta-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.4rem;
            margin-bottom: 0.6rem;
        }
        .argus-domain-badge {
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            background-color: #f0f2f6;
            border: 1px solid #d0d4da;
            color: #374151;
            border-radius: 999px;
            padding: 0.15rem 0.6rem;
        }
        .argus-scraped-badge {
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            border-radius: 999px;
            padding: 0.15rem 0.6rem;
        }
        .argus-scraped-badge--yes {
            background-color: #f1f9f3;
            border: 1px solid #bfe3c8;
            color: #1f7a3d;
        }
        .argus-scraped-badge--no {
            background-color: #f0f2f6;
            border: 1px solid #d0d4da;
            color: #6b7280;
        }
        .argus-source-id-badge {
            display: inline-block;
            font-size: 0.72rem;
            font-family: monospace;
            background-color: #ffffff;
            border: 1px solid #d0d4da;
            border-radius: 5px;
            padding: 0.1rem 0.5rem;
            color: #6b7280;
        }
        .argus-url-label {
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            color: #6b7280;
            text-transform: uppercase;
            margin-bottom: 0.2rem;
        }
        .argus-url-box {
            background-color: #f8f9fb;
            border: 1px solid #e3e6eb;
            border-radius: 6px;
            padding: 0.45rem 0.7rem;
            margin-bottom: 0.6rem;
            font-size: 0.85rem;
            word-break: break-all;
            overflow-wrap: anywhere;
        }
        .argus-url-box a {
            color: #2563eb;
            text-decoration: none;
        }
        .argus-url-box a:hover {
            text-decoration: underline;
        }
        .argus-snippet-label {
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            color: #6b7280;
            text-transform: uppercase;
            margin-bottom: 0.2rem;
        }
        .argus-snippet-box {
            background-color: #f8f9fb;
            border-left: 3px solid #9aa0ab;
            border-radius: 4px;
            padding: 0.6rem 0.85rem;
            font-size: 0.87rem;
            font-style: italic;
            color: #31333f;
            line-height: 1.5;
            word-break: break-word;
            overflow-wrap: anywhere;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if not state.sources:

        st.markdown(
            '<div class="argus-empty-state">No sources were retrieved.</div>',
            unsafe_allow_html=True,
        )

    for source in state.sources:

        # Source ID is only shown if the underlying object already
        # exposes one — no identifier is invented if it's absent.
        source_id = getattr(source, "id", None)

        # The collapsed expander label is truncated so a very long
        # title or URL can't stretch or break the layout; the full,
        # untruncated title/URL is still shown inside the card.
        source_label = source.title or source.url
        if len(source_label) > 80:
            source_label = source_label[:77] + "..."

        with st.expander(source_label):

            st.markdown(
                f'<div class="argus-source-title">{source.title or source.url}</div>',
                unsafe_allow_html=True,
            )

            scraped_class = (
                "argus-scraped-badge--yes"
                if source.has_content
                else "argus-scraped-badge--no"
            )
            scraped_label = (
                "Scraped" if source.has_content else "Not scraped"
            )

            meta_badges = [
                f'<span class="argus-domain-badge">{source.domain}</span>',
                f'<span class="argus-scraped-badge {scraped_class}">'
                f"{scraped_label}</span>",
            ]
            if source_id:
                meta_badges.append(
                    f'<span class="argus-source-id-badge">ID: {source_id}</span>'
                )

            st.markdown(
                f'<div class="argus-source-meta-row">{"".join(meta_badges)}</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="argus-url-label">URL</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="argus-url-box">'
                f'<a href="{source.url}" target="_blank" rel="noopener noreferrer">'
                f"{source.url}</a></div>",
                unsafe_allow_html=True,
            )

            if source.snippet:

                st.markdown(
                    '<div class="argus-snippet-label">Snippet</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="argus-snippet-box">{source.snippet}</div>',
                    unsafe_allow_html=True,
                )

    # ============================================================
    # EVIDENCE GRAPH
    # ============================================================

    st.divider()
    st.header("🕸️ Evidence Graph")

    st.caption(
        "This graph traces how the investigation connects to the "
        "claims it produced, and how each claim connects to the "
        "sources that support or contradict it — including where "
        "supporting and contradicting evidence appears."
    )

    # ------------------------------------------------------------
    # Legend (presentation only). The meanings below are read
    # directly off the existing DOT styling further down — ellipse
    # nodes, box nodes, note-shaped nodes, and the gray/green/red
    # dashed edge colors — none of which are changed here. This
    # replaces squinting at the small in-graph legend node with a
    # clearer version above the chart; the in-graph legend node
    # itself is left exactly as the existing DOT data builds it.
    # ------------------------------------------------------------

    st.markdown(
        """
        <style>
        .argus-graph-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin: 0.5rem 0 1.1rem 0;
        }
        .argus-graph-legend-item {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            font-size: 0.8rem;
            color: #374151;
            background-color: #f8f9fb;
            border: 1px solid #e3e6eb;
            border-radius: 6px;
            padding: 0.3rem 0.7rem;
        }
        .argus-graph-legend-glyph {
            font-size: 0.9rem;
        }
        .argus-graph-legend-line {
            display: inline-block;
            width: 1.1rem;
            height: 0;
            border-top: 2px solid;
        }
        .argus-graph-legend-line--dashed {
            border-top-style: dashed;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="argus-graph-legend">'
        '<div class="argus-graph-legend-item">'
        '<span class="argus-graph-legend-glyph">⬭</span> Investigation node'
        "</div>"
        '<div class="argus-graph-legend-item">'
        '<span class="argus-graph-legend-glyph">▭</span> Claim node'
        "</div>"
        '<div class="argus-graph-legend-item">'
        '<span class="argus-graph-legend-glyph">🗒</span> Source node'
        "</div>"
        '<div class="argus-graph-legend-item">'
        '<span class="argus-graph-legend-line" '
        'style="border-color:gray;"></span> Investigates'
        "</div>"
        '<div class="argus-graph-legend-item">'
        '<span class="argus-graph-legend-line" '
        'style="border-color:green;"></span> Supports'
        "</div>"
        '<div class="argus-graph-legend-item">'
        '<span class="argus-graph-legend-line argus-graph-legend-line--dashed" '
        'style="border-color:red;"></span> Contradicts'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
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
    # CONTRADICTIONS
    # ============================================================
    # Presentation only — state.contradictions is read exactly as
    # produced by the pipeline; nothing here detects, creates,
    # scores, or explains contradictions.

    st.divider()
    st.header("⚡ Contradictions")

    st.markdown(
        """
        <style>
        .argus-contradiction-card {
            background-color: #fdf2f2;
            border: 1px solid #f3b4b4;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.6rem;
        }
        .argus-contradiction-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            color: #b3261e;
            margin-bottom: 0.3rem;
        }
        .argus-contradiction-text {
            font-size: 0.9rem;
            color: #31333f;
            line-height: 1.5;
            word-break: break-word;
        }
        .argus-contradiction-none {
            background-color: #f1f9f3;
            border: 1px solid #bfe3c8;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.9rem;
            color: #1f7a3d;
        }
        .argus-task-card {
            background-color: #f8f9fb;
            border: 1px solid #e3e6eb;
            border-left: 3px solid #d0d4da;
            border-radius: 8px;
            padding: 0.7rem 1rem;
            margin-bottom: 0.55rem;
        }
        .argus-task-text {
            font-size: 0.9rem;
            color: #31333f;
            line-height: 1.5;
            word-break: break-word;
        }
        .argus-task-badges {
            margin-top: 0.4rem;
        }
        .argus-task-badge {
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            background-color: #f0f2f6;
            border: 1px solid #d0d4da;
            color: #374151;
            border-radius: 999px;
            padding: 0.12rem 0.55rem;
            margin-right: 0.35rem;
        }
        .argus-task-none {
            background-color: #f1f9f3;
            border: 1px solid #bfe3c8;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.9rem;
            color: #1f7a3d;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if state.contradictions:

        for _idx, _contradiction in enumerate(state.contradictions, start=1):

            st.markdown(
                '<div class="argus-contradiction-card">'
                f'<div class="argus-contradiction-label">'
                f"Contradiction {_idx}</div>"
                f'<div class="argus-contradiction-text">{_contradiction}</div>'
                "</div>",
                unsafe_allow_html=True,
            )

    else:

        st.markdown(
            '<div class="argus-contradiction-none">'
            "No contradictions detected.</div>",
            unsafe_allow_html=True,
        )

    # ============================================================
    # VERIFICATION TASKS
    # ============================================================
    # Presentation only — state.verification_tasks is read exactly
    # as produced by the pipeline; task creation logic is untouched.

    st.divider()
    st.header("🔍 Verification Tasks")

    if state.verification_tasks:

        for task in state.verification_tasks:

            # Status/priority badges are shown ONLY if the task
            # object already exposes those fields — none are
            # invented when absent (plain-string tasks show no
            # badges at all).
            task_status = getattr(task, "status", None)
            task_priority = getattr(task, "priority", None)

            badge_html = ""
            if task_status:
                badge_html += (
                    f'<span class="argus-task-badge">{task_status}</span>'
                )
            if task_priority:
                badge_html += (
                    f'<span class="argus-task-badge">{task_priority}</span>'
                )

            badges_block = (
                f'<div class="argus-task-badges">{badge_html}</div>'
                if badge_html
                else ""
            )

            st.markdown(
                '<div class="argus-task-card">'
                f'<div class="argus-task-text">☐ {task}</div>'
                f"{badges_block}"
                "</div>",
                unsafe_allow_html=True,
            )

    else:

        st.markdown(
            '<div class="argus-task-none">'
            "No additional verification tasks required.</div>",
            unsafe_allow_html=True,
        )

    # ============================================================
    # UNRESOLVED ISSUES
    # ============================================================

    st.divider()
    st.header("⚠️ Unresolved Issues")

    if state.unresolved_questions:

        for issue in state.unresolved_questions:

            st.error(
                issue
            )

    else:

        st.markdown(
            '<div class="argus-task-none">No unresolved issues.</div>',
            unsafe_allow_html=True,
        )