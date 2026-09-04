from models.investigation import Investigation
from models.sources import Source
from tools.anakin_search import search_web


def investigate(query: str, limit: int = 5) -> Investigation:
    """
    Search the web and convert the results into an Investigation.
    """

    results = search_web(query, limit=limit)

    sources = [
        Source(
            title=result.title,
            url=result.url,
            snippet=result.snippet,
            date=result.date,
            last_updated=result.last_updated,
        )
        for result in results
    ]

    return Investigation(
        query=query,
        sources=sources,
    )