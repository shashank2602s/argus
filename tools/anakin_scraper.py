import os
import time
from dataclasses import dataclass
from typing import Any, Optional

import requests
from dotenv import load_dotenv


load_dotenv()

ANAKIN_SCRAPER_URL = "https://api.anakin.io/v1/url-scraper"


@dataclass
class ScrapedPage:
    url: str
    title: str
    content: str
    structured: Optional[Any] = None
    success: bool = True
    error: Optional[str] = None


def scrape_url(
    url: str,
    generate_json: bool = False,
    timeout: int = 180,
) -> ScrapedPage:
    """
    Submit a URL to Anakin and poll until the scrape is complete.
    """

    api_key = os.getenv("ANAKIN_API_KEY")

    if not api_key:
        raise ValueError(
            "ANAKIN_API_KEY is not set. Add your API key to the .env file."
        )

    if not url or not url.strip():
        raise ValueError("URL cannot be empty.")

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "url": url.strip(),
        "generateJson": generate_json,
    }

    try:
        response = requests.post(
            ANAKIN_SCRAPER_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )
    except requests.Timeout as exc:
        return ScrapedPage(
            url=url,
            title="",
            content="",
            success=False,
            error="Anakin scraper request timed out.",
        )
    except requests.RequestException as exc:
        return ScrapedPage(
            url=url,
            title="",
            content="",
            success=False,
            error=f"Network error while contacting Anakin: {exc}",
        )

    if response.status_code in (401, 403):
        raise RuntimeError(
            "Anakin API authentication failed. Check your API key."
        )

    if response.status_code == 402:
        raise RuntimeError("Anakin API credits are insufficient.")

    if response.status_code == 429:
        raise RuntimeError(
            "Anakin API rate limit exceeded. Try again later."
        )

    if response.status_code >= 500:
        raise RuntimeError(
            f"Anakin API server error (HTTP {response.status_code})."
        )

    if not response.ok:
        return ScrapedPage(
            url=url,
            title="",
            content="",
            success=False,
            error=f"Anakin scraper request failed (HTTP {response.status_code}).",
        )

    try:
        data = response.json()
    except ValueError as exc:
        return ScrapedPage(
            url=url,
            title="",
            content="",
            success=False,
            error="Anakin returned invalid JSON.",
        )

    job_id = data.get("jobId")

    if not job_id:
        return ScrapedPage(
            url=url,
            title="",
            content="",
            success=False,
            error="Anakin response did not contain a jobId.",
        )

    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            result_response = requests.get(
                f"{ANAKIN_SCRAPER_URL}/{job_id}",
                headers={"X-API-Key": api_key},
                timeout=30,
            )
        except requests.RequestException:
            time.sleep(3)
            continue

        if result_response.status_code in (401, 403):
            raise RuntimeError(
                "Anakin API authentication failed while polling."
            )

        if result_response.status_code == 429:
            raise RuntimeError(
                "Anakin API rate limit exceeded while polling."
            )

        if result_response.status_code >= 500:
            time.sleep(3)
            continue

        if not result_response.ok:
            return ScrapedPage(
                url=url,
                title="",
                content="",
                success=False,
                error=(
                    "Anakin polling request failed "
                    f"(HTTP {result_response.status_code})."
                ),
            )

        try:
            job = result_response.json()
        except ValueError:
            time.sleep(3)
            continue

        status = job.get("status")

        if status == "completed":
            return _parse_scrape_result(url, job)

        if status == "failed":
            return ScrapedPage(
                url=url,
                title="",
                content="",
                success=False,
                error=str(job.get("error", "Scraping failed.")),
            )

        time.sleep(3)

    return ScrapedPage(
        url=url,
        title="",
        content="",
        success=False,
        error="Scraping timed out while waiting for Anakin.",
    )


def _parse_scrape_result(url: str, data: dict) -> ScrapedPage:
    """
    Convert Anakin's completed scrape response into ScrapedPage.
    """

    content = str(data.get("markdown", ""))

    if not content:
        content = str(data.get("cleanedHtml", ""))

    title = str(data.get("title", ""))

    if not title and content:
        first_line = content.splitlines()[0].strip()
        if first_line.startswith("#"):
            title = first_line.lstrip("#").strip()

    return ScrapedPage(
        url=url,
        title=title,
        content=content,
        structured=data.get("generatedJson"),
        success=True,
    )


def scrape_urls(
    urls: list[str],
    generate_json: bool = False,
    delay_between_calls: float = 0.0,
) -> list[ScrapedPage]:
    """
    Scrape multiple URLs.
    """

    results = []

    for index, url in enumerate(urls):
        result = scrape_url(
            url,
            generate_json=generate_json,
        )

        results.append(result)

        if delay_between_calls > 0 and index < len(urls) - 1:
            time.sleep(delay_between_calls)

    return results