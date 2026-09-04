import re

from models.claims import Claim
from models.investigation import Investigation


STOP_WORDS = {
    "about",
    "after",
    "against",
    "among",
    "because",
    "being",
    "could",
    "from",
    "have",
    "into",
    "more",
    "other",
    "over",
    "reported",
    "reports",
    "said",
    "that",
    "their",
    "there",
    "these",
    "this",
    "those",
    "through",
    "will",
    "with",
    "would",
}


def _meaningful_words(text: str) -> set[str]:
    """Return normalized content words from a claim."""

    words = re.findall(r"[a-zA-Z0-9]+", text.lower())

    return {
        word
        for word in words
        if len(word) >= 5 and word not in STOP_WORDS
    }


def _similarity(claim_a: Claim, claim_b: Claim) -> float:
    """Calculate simple word-overlap similarity between two claims."""

    words_a = _meaningful_words(claim_a.statement)
    words_b = _meaningful_words(claim_b.statement)

    if not words_a or not words_b:
        return 0.0

    intersection = words_a & words_b
    union = words_a | words_b

    return len(intersection) / len(union)


def _merge_claims(base: Claim, other: Claim) -> None:
    """Merge evidence from another matching claim."""

    for source_id in other.source_ids:
        if source_id not in base.source_ids:
            base.source_ids.append(source_id)

    for source_id in other.supporting_sources:
        if source_id not in base.supporting_sources:
            base.supporting_sources.append(source_id)


def match_claims(
    investigation: Investigation,
    threshold: float = 0.30,
) -> Investigation:
    """
    Group similar claims from independent sources.

    Claims with sufficient word overlap are treated as evidence
    supporting the same underlying factual claim.
    """

    claims = investigation.claims

    for index, base_claim in enumerate(claims):

        for other_claim in claims[index + 1:]:

            if base_claim.id == other_claim.id:
                continue

            base_sources = set(base_claim.source_ids)
            other_sources = set(other_claim.source_ids)

            # Never merge claims originating from the same source.
            if base_sources & other_sources:
                continue

            similarity = _similarity(
                base_claim,
                other_claim,
            )

            if similarity >= threshold:
                _merge_claims(
                    base_claim,
                    other_claim,
                )

                _merge_claims(
                    other_claim,
                    base_claim,
                )

    return investigation