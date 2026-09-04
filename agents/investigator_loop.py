from datetime import datetime, timezone

from agents.claim_extractor import extract_claims
from agents.verifier import verify_claims
from agents.state import InvestigationState
from models.sources import Source
from tools.anakin_search import search_web
from tools.anakin_scraper import scrape_urls


MAX_RESULTS_PER_QUERY = 5
MAX_SOURCES_TO_SCRAPE = 8
MAX_SOURCES_PER_DOMAIN = 2


def _select_sources(
    sources: list[Source],
    limit: int = MAX_SOURCES_TO_SCRAPE,
) -> list[Source]:
    """Select the best sources while limiting one domain from dominating."""

    selected = []
    domain_counts = {}

    # Higher relevance first.
    ranked_sources = sorted(
        sources,
        key=lambda source: source.relevance_score,
        reverse=True,
    )

    for source in ranked_sources:
        domain = source.domain

        if domain_counts.get(domain, 0) >= MAX_SOURCES_PER_DOMAIN:
            continue

        selected.append(source)
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

        if len(selected) >= limit:
            break

    return selected


def run_search_phase(state: InvestigationState) -> InvestigationState:
    """Run all planned search queries and collect unique sources."""

    for query in state.search_queries:
        try:
            results = search_web(
                query,
                limit=MAX_RESULTS_PER_QUERY,
            )

            for rank, result in enumerate(results, start=1):
                source = Source(
                    id=f"source-{len(state.sources) + 1}",
                    url=result.url,
                    title=result.title,
                    snippet=result.snippet,
                    retrieved_at=datetime.now(timezone.utc).isoformat(),
                    publication_date=result.date,
                    relevance_score=1.0 / rank,
                )

                state.add_source(source)

        except Exception as exc:
            state.unresolved_questions.append(
                f"Search failed for '{query}': {exc}"
            )

    return state


def run_scrape_phase(state: InvestigationState) -> InvestigationState:
    """Scrape the best selected sources."""

    selected_sources = _select_sources(state.sources)

    if not selected_sources:
        state.unresolved_questions.append(
            "No sources were available for scraping."
        )
        return state

    try:
        pages = scrape_urls(
            [source.url for source in selected_sources]
        )

        pages_by_url = {
            page.url: page
            for page in pages
        }

        for source in selected_sources:
            page = pages_by_url.get(source.url)

            if page and page.success:
                source.content = page.content

                if page.title:
                    source.title = page.title

            else:
                state.unresolved_questions.append(
                    f"Could not scrape source: {source.url}"
                )

    except Exception as exc:
        state.unresolved_questions.append(
            f"Scraping phase failed: {exc}"
        )

    return state


def run_extraction_phase(
    state: InvestigationState,
) -> InvestigationState:
    """Extract and verify claims from scraped sources."""

    # Reuse the existing deterministic claim extractor.
    investigation = extract_claims(
        type(
            "InvestigationContainer",
            (),
            {
                "sources": state.sources,
                "claims": state.claims,
            },
        )()
    )

    state.claims = investigation.claims

    # Reuse the existing verifier.
    investigation = verify_claims(
        type(
            "InvestigationContainer",
            (),
            {
                "sources": state.sources,
                "claims": state.claims,
            },
        )()
    )

    state.claims = investigation.claims

    return state


def investigate_loop(state: InvestigationState) -> InvestigationState:
    """
    Run one complete ARGUS investigation pass.

    Pipeline:
        Search → Select Sources → Scrape → Extract Claims → Verify
    """

    state = run_search_phase(state)
    state = run_scrape_phase(state)
    state = run_extraction_phase(state)

    state.usage_stats["search_queries"] = len(
        state.search_queries
    )
    state.usage_stats["sources_found"] = len(
        state.sources
    )
    state.usage_stats["sources_scraped"] = sum(
        1 for source in state.sources
        if source.has_content
    )
    state.usage_stats["claims_extracted"] = len(
        state.claims
    )

    return state