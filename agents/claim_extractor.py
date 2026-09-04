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
    r"%"
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


def _clean_sentence(sentence: str) -> str:
    """Remove common scraped webpage artifacts."""

    # Remove Markdown images.
    sentence = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", sentence)

    # Remove Markdown links but keep their visible text.
    sentence = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", sentence)

    # Remove URLs.
    sentence = re.sub(r"https?://\S+", "", sentence)

    # Remove Markdown table separators.
    if re.fullmatch(r"\s*\|?[\s\-:|]+\|?\s*", sentence):
        return ""

    # Remove leading Markdown heading markers.
    sentence = re.sub(r"^\s*#{1,6}\s*", "", sentence)

    # Remove common table formatting.
    sentence = sentence.replace("|", " ")

    # Remove excessive whitespace.
    sentence = re.sub(r"\s+", " ", sentence)

    return sentence.strip(" -•\t\r\n")


def _looks_like_claim(sentence: str) -> bool:
    """Return True when a sentence looks like a useful factual claim."""

    if len(sentence) < 50 or len(sentence) > 500:
        return False

    lower = sentence.lower()

    if any(phrase in lower for phrase in SKIP_PHRASES):
        return False

    # Reject obvious metadata/table fragments.
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
    ]

    if any(word in lower for word in metadata_words):
        return False

    has_claim_pattern = any(
        re.search(pattern, lower)
        for pattern in CLAIM_PATTERNS
    )

    if not has_claim_pattern:
        return False

    has_number = bool(
        re.search(r"\b\d+(?:\.\d+)?%?\b", sentence)
    )

    has_year = bool(
        re.search(r"\b20\d{2}\b", sentence)
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

    return has_number or has_year or has_reporting_language


def extract_claims(investigation: Investigation) -> Investigation:
    """
    Extract candidate factual claims from scraped source content.

    This is a deterministic first version and does not use an LLM.
    """

    claims: List[Claim] = []

    for source in investigation.sources:
        if not source.content.strip():
            continue

        sentences = re.split(
            r"(?<=[.!?])\s+",
            source.content
        )

        source_claim_count = 0

        for sentence in sentences:
            sentence = _clean_sentence(sentence)

            if not sentence:
                continue

            if not _looks_like_claim(sentence):
                continue

            claim_id = f"claim-{len(claims) + 1}"

            claim = Claim(
                id=claim_id,
                statement=sentence,
                source_ids=[source.id],
                evidence_excerpt=sentence,
                entities=[],
                supporting_sources=[source.id],
                confidence=0.0,
                status=ClaimStatus.UNVERIFIED,
            )

            claims.append(claim)
            source_claim_count += 1

            if source_claim_count >= 10:
                break

    investigation.claims = claims

    return investigation