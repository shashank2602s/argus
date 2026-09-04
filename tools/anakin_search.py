import os
from dataclasses import dataclass
from typing import Optional

import requests
from dotenv import load_dotenv


load_dotenv()

ANAKIN_SEARCH_URL = "https://api.anakin.io/v1/search"


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    date: Optional[str] = None
    last_updated: Optional[str] = None


def search_web(query: str, limit: int = 5, timeout: int = 15) -> list[SearchResult]:
    """
    Search the web using the Anakin Search API.

    Args:
        query: The search query.
        limit: Maximum number of results to return.
        timeout: HTTP request timeout in seconds.

    Returns:
        A list of SearchResult objects.

    Raises:
        ValueError: If the query, limit, or API key is invalid.
        RuntimeError: If the Anakin API request fails.
    """

    api_key = os.getenv("ANAKIN_API_KEY")

    if not api_key:
        raise ValueError(
            "ANAKIN_API_KEY is not set. Add your API key to the .env file."
        )

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if limit < 1:
        raise ValueError("limit must be at least 1.")

    payload = {
        "prompt": query.strip(),
        "limit": limit,
    }

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            ANAKIN_SEARCH_URL,
            json=payload,
            headers=headers,
            timeout=timeout,
        )

    except requests.Timeout as exc:
        raise RuntimeError("Anakin Search request timed out.") from exc

    except requests.RequestException as exc:
        raise RuntimeError(f"Network error while contacting Anakin: {exc}") from exc

    if response.status_code == 401 or response.status_code == 403:
        raise RuntimeError("Anakin API authentication failed. Check your API key.")

    if response.status_code == 402:
        raise RuntimeError("Anakin API credits are insufficient.")

    if response.status_code == 429:
        raise RuntimeError("Anakin API rate limit exceeded. Try again later.")

    if response.status_code >= 500:
        raise RuntimeError(
            f"Anakin API server error (HTTP {response.status_code})."
        )

    if response.status_code == 400:
        raise RuntimeError("Anakin API rejected the search request (HTTP 400).")

    if not response.ok:
        raise RuntimeError(
            f"Anakin API request failed (HTTP {response.status_code})."
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("Anakin returned an invalid JSON response.") from exc

    results = data.get("results")

    if not isinstance(results, list):
        raise RuntimeError("Anakin response does not contain a valid results list.")

    parsed_results = []

    for item in results:
        if not isinstance(item, dict):
            continue

        parsed_results.append(
            SearchResult(
                title=str(item.get("title", "")),
                url=str(item.get("url", "")),
                snippet=str(item.get("snippet", "")),
                date=item.get("date"),
                last_updated=item.get("last_updated"),
            )
        )

    return parsed_results