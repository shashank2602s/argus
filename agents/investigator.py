from datetime import datetime, timezone

from models.investigation import Investigation
from models.sources import Source
from tools.anakin_search import search_web
from tools.anakin_scraper import scrape_urls


def investigate(query: str, limit: int = 5) -> Investigation:
    results = search_web(query, limit=limit)

    sources = [
        Source(
            id=f"source-{index}",
            url=result.url,
            title=result.title,
            snippet=result.snippet,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            publication_date=result.date,
        )
        for index, result in enumerate(results, start=1)
    ]

    if not sources:
        return Investigation(
            query=query,
            sources=[],
        )

    scraped_pages = scrape_urls([source.url for source in sources])

    scraped_by_url = {
        page.url: page
        for page in scraped_pages
    }

    for source in sources:
        page = scraped_by_url.get(source.url)

        if page and page.success:
            source.content = page.content

            if page.title:
                source.title = page.title

    return Investigation(
        query=query,
        sources=sources,
    )