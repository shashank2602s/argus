import re
from typing import List

from models.claims import Claim, ClaimStatus
from models.investigation import Investigation


CLAIM_PATTERNS = [
    r"\baccording to\b",
    r"\breported that\b",
    r"\breports that\b",
    r"\bfound that\b",
    r"\bshows that\b",
    r"\brevealed that\b",
    r"\bannounced that\b",
    r"\bsaid that\b",
    r"\bexpects\b",
    r"\bexpected\b",
    r"\bprojected\b",
    r"\bincreased\b",
    r"\bdecreased\b",
    r"\bgrowing\b",
    r"\bgrowth\b",
    r"\bpercent\b",
    r"%",
]


SKIP_PHRASES = [
    "we provide",
    "we help",
    "our mission",
    "our vision",
    "our goal",
    "learn more",
    "read more",
    "subscribe",
    "cookie",
    "privacy policy",
    "terms of use",
    "sign in",
    "log in",
    "contact us",
    "about us",
    "click here",
    "get started",
]


HEADER_PHRASES = [
    "analysts to explore",
    "sign up",
    "register now",
    "join us",
    "press release",
    "media contact",
]


def _clean_sentence(sentence: str) -> str:
    """
    Clean common Markdown, URL, HTML, and scraped webpage artifacts.
    """

    sentence = re.sub(
        r"!\[[^\]]*\]\([^)]+\)",
        "",
        sentence,
    )

    sentence = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        sentence,
    )

    sentence = re.sub(
        r"\[([^\]]+)\]\\\([^)]+\\\)",
        r"\1",
        sentence,
    )

    sentence = re.sub(
        r"https?://\S+",
        "",
        sentence,
    )

    sentence = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        sentence,
    )

    sentence = re.sub(
        r"(\*\*|__|\*|_)",
        "",
        sentence,
    )

    sentence = sentence.replace("\\", "")
    sentence = sentence.replace("|", " ")
    sentence = sentence.replace("[", "")
    sentence = sentence.replace("]", "")

    sentence = re.sub(
        r"\btrend\s+s\b",
        "trends",
        sentence,
        flags=re.IGNORECASE,
    )

    sentence = re.sub(
        r"\bthreat\s+landscape\b",
        "threat landscape",
        sentence,
        flags=re.IGNORECASE,
    )

    sentence = re.sub(
        r"\s+",
        " ",
        sentence,
    )

    return sentence.strip(
        " -•–—:;\t\r\n"
    )


def _remove_article_header(text: str) -> str:
    """
    Remove common article-header material that frequently appears
    before the actual factual statement in scraped pages.
    """

    text = re.sub(
        r"\b(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{1,2},\s+20\d{2}\b",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\b[A-Z][A-Z\s]+,\s*[A-Z][a-z]+,\s*"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{1,2},\s+20\d{2}\b",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\bAnalysts to Explore\b.*?(?=\bThe chaotic rise\b|\bThe rise\b|\bThe growing\b)",
        "",
        text,
        flags=re.IGNORECASE,
    )

    title_patterns = [
        r"^Gartner Identifies the Top Cybersecurity Trends for 2026\s*",
        r"^Gartner Identifies.*?2026\s*",
    ]

    for pattern in title_patterns:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE,
        )

    factual_starts = [
        "The chaotic rise",
        "The rise",
        "The growing",
        "The increasing",
        "Cybersecurity attacks",
        "Cyber spending",
        "AI-enabled threats",
        "Artificial intelligence",
        "By 2025",
        "By 2026",
    ]

    lower_text = text.lower()

    positions = []

    for marker in factual_starts:
        index = lower_text.find(marker.lower())

        if index >= 0:
            positions.append(index)

    if positions:
        first_position = min(positions)

        if first_position > 0:
            text = text[first_position:]

    return text.strip()


def _extract_factual_sentence(text: str) -> str:
    """
    Extract the most useful factual sentence from a scraped text block.
    """

    text = _clean_sentence(text)

    if not text:
        return ""

    text = _remove_article_header(text)

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    if not text:
        return ""

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        if _looks_like_claim(sentence):
            return sentence

    markers = [
        "The chaotic rise",
        "The rise",
        "The growing",
        "The increasing",
        "Cybersecurity attacks",
        "Cyber spending",
        "AI-enabled threats",
        "Artificial intelligence",
        "By 2025",
        "By 2026",
    ]

    lower_text = text.lower()

    for marker in markers:

        index = lower_text.find(marker.lower())

        if index >= 0:

            candidate = text[index:].strip()

            candidate = re.split(
                r"\b(?:Analysts to Explore|Learn More|Subscribe)\b",
                candidate,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip()

            if len(candidate) >= 50:

                if len(candidate) > 350:
                    candidate = (
                        candidate[:347]
                        + "..."
                    )

                return candidate

    return ""


def _normalize_claim(sentence: str) -> str:
    """
    Normalize a factual claim for display.
    """

    sentence = _clean_sentence(sentence)

    if not sentence:
        return ""

    sentence = re.sub(
        r"^\s*(stat/figure|statistic|figure|key finding)\s*[:\-–—]\s*",
        "",
        sentence,
        flags=re.IGNORECASE,
    )

    sentence = re.sub(
        r"^[\s:;,\-–—]+",
        "",
        sentence,
    )

    sentence = re.sub(
        r"^Gartner Identifies the Top Cybersecurity Trends for 2026\s*",
        "",
        sentence,
        flags=re.IGNORECASE,
    )

    sentence = re.sub(
        r"\btrend\s+s\b",
        "trends",
        sentence,
        flags=re.IGNORECASE,
    )

    sentence = re.sub(
        r"\bcybersecurity\s+trend\s+s\b",
        "cybersecurity trends",
        sentence,
        flags=re.IGNORECASE,
    )

    sentence = re.sub(
        r"\s+",
        " ",
        sentence,
    ).strip()

    sentence = re.sub(
        r"\s+\.\.\.$",
        "...",
        sentence,
    )

    if sentence and sentence[-1] not in ".!?":
        sentence += "."

    return sentence


def _looks_like_claim(sentence: str) -> bool:
    """
    Return True when a sentence looks like a useful factual claim.
    """

    if len(sentence) < 50:
        return False

    if len(sentence) > 500:
        return False

    lower = sentence.lower()

    if any(
        phrase in lower
        for phrase in SKIP_PHRASES
    ):
        return False

    metadata_words = [
        "product details",
        "attribute",
        "image",
        "filename",
        "file name",
        "download",
        "pdf",
        "jpg",
        "png",
        "javascript",
        "all rights reserved",
    ]

    if any(
        word in lower
        for word in metadata_words
    ):
        return False

    if any(
        phrase in lower
        for phrase in HEADER_PHRASES
    ):
        return False

    if lower.startswith(
        "gartner identifies the top"
    ):
        return False

    has_claim_pattern = any(
        re.search(
            pattern,
            lower,
        )
        for pattern in CLAIM_PATTERNS
    )

    if not has_claim_pattern:
        return False

    has_number = bool(
        re.search(
            r"\b\d+(?:\.\d+)?%?\b",
            sentence,
        )
    )

    has_year = bool(
        re.search(
            r"\b20\d{2}\b",
            sentence,
        )
    )

    has_reporting_language = any(
        phrase in lower
        for phrase in [
            "according to",
            "reported",
            "reports",
            "found that",
            "revealed",
            "announced",
            "expects",
            "projected",
        ]
    )

    return (
        has_number
        or has_year
        or has_reporting_language
    )


def _build_evidence_excerpt(
    statement: str,
) -> str:
    """
    Build a clean evidence excerpt from the normalized
    factual claim.
    """

    excerpt = _clean_sentence(statement)

    excerpt = _remove_article_header(excerpt)

    excerpt = re.sub(
        r"\s+",
        " ",
        excerpt,
    ).strip()

    if len(excerpt) > 600:
        excerpt = (
            excerpt[:597]
            + "..."
        )

    return excerpt


def extract_claims(
    investigation: Investigation,
) -> Investigation:
    """
    Extract candidate factual claims from scraped source content.

    source_ids:
        Sources where the claim was found.

    supporting_sources:
        Independent sources that corroborate the claim.
        These are added later by claim matching.
    """

    claims: List[Claim] = []

    for source in investigation.sources:

        if not source.content.strip():
            continue

        raw_chunks = re.split(
            r"\n+|(?<=[.!?])\s+",
            source.content,
        )

        source_claim_count = 0

        for raw_chunk in raw_chunks:

            if not raw_chunk.strip():
                continue

            cleaned = _clean_sentence(
                raw_chunk
            )

            if not cleaned:
                continue

            lower_cleaned = cleaned.lower()

            if lower_cleaned.startswith(
                "gartner identifies the top"
            ):
                continue

            if any(
                phrase in lower_cleaned
                for phrase in HEADER_PHRASES
            ):
                continue

            factual_sentence = (
                _extract_factual_sentence(
                    cleaned
                )
            )

            if not factual_sentence:
                continue

            if not _looks_like_claim(
                factual_sentence
            ):
                continue

            statement = _normalize_claim(
                factual_sentence
            )

            if not statement:
                continue

            evidence_excerpt = (
                _build_evidence_excerpt(
                    statement
                )
            )

            if not evidence_excerpt:
                continue

            duplicate = any(
                existing.statement.lower()
                == statement.lower()
                for existing in claims
            )

            if duplicate:
                continue

            claim_id = (
                f"claim-{len(claims) + 1}"
            )

            claim = Claim(
                id=claim_id,
                statement=statement,
                source_ids=[source.id],
                evidence_excerpt=evidence_excerpt,
                entities=[],

                # IMPORTANT:
                # The source where we found the claim is NOT
                # automatically an independent corroborating source.
                # The matcher adds independent supporting sources.
                supporting_sources=[],

                confidence=0.0,
                status=ClaimStatus.UNVERIFIED,
            )

            claims.append(claim)

            source_claim_count += 1

            if source_claim_count >= 10:
                break

    investigation.claims = claims

    return investigation