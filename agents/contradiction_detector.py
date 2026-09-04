from models.claims import ClaimStatus
from models.investigation import Investigation


CONTRADICTION_PAIRS = [
    # Change / trend
    ("increased", "decreased"),
    ("increase", "decrease"),
    ("increasing", "decreasing"),
    ("grew", "declined"),
    ("growth", "decline"),
    ("grew", "fell"),
    ("rise", "fall"),
    ("rising", "falling"),
    ("higher", "lower"),
    ("more", "less"),
    ("up", "down"),

    # Risk / impact
    ("higher risk", "lower risk"),
    ("high risk", "low risk"),
    ("increased risk", "reduced risk"),
    ("greater risk", "lower risk"),
    ("more vulnerable", "less vulnerable"),
    ("vulnerable", "protected"),

    # Security outcomes
    ("effective", "ineffective"),
    ("effective", "ineffective"),
    ("successful", "unsuccessful"),
    ("prevented", "failed"),
    ("mitigated", "unmitigated"),
    ("secure", "insecure"),

    # General conclusions
    ("positive", "negative"),
    ("supports", "rejects"),
    ("supported", "unsupported"),
    ("confirmed", "disputed"),
    ("confirmed", "denied"),
    ("true", "false"),
]


def _contains_opposing_language(text_a: str, text_b: str) -> bool:
    """Check whether two pieces of text contain opposing language."""

    a = text_a.lower()
    b = text_b.lower()

    for first, second in CONTRADICTION_PAIRS:
        if first in a and second in b:
            return True

        if second in a and first in b:
            return True

    return False


def _meaningful_words(text: str) -> set[str]:
    """Return normalized words useful for comparing claims."""

    return {
        word.lower().strip(".,:;!?()[]{}\"'")
        for word in text.split()
        if len(word) >= 5
    }


def _claims_discuss_same_topic(
    statement_a: str,
    statement_b: str,
) -> bool:
    """Check whether two claims share enough meaningful words."""

    words_a = _meaningful_words(statement_a)
    words_b = _meaningful_words(statement_b)

    overlap = words_a & words_b

    return len(overlap) >= 2


def detect_contradictions(
    investigation: Investigation,
) -> Investigation:
    """
    Detect basic contradictions between claims from different sources.

    This deterministic version:
    1. Compares claims from different sources.
    2. Checks whether they discuss a similar topic.
    3. Looks for opposing language.
    4. Marks both claims as contested when a contradiction is found.
    """

    # Preserve the original source relationships before modifying claims.
    original_source_ids = {
        claim.id: set(claim.source_ids)
        for claim in investigation.claims
    }

    for claim in investigation.claims:
        claim_sources = original_source_ids[claim.id]

        for other_claim in investigation.claims:
            if claim.id == other_claim.id:
                continue

            other_sources = original_source_ids[other_claim.id]

            # Claims from the same original source are not contradictions.
            if claim_sources & other_sources:
                continue

            # The claims must discuss a sufficiently similar topic.
            if not _claims_discuss_same_topic(
                claim.statement,
                other_claim.statement,
            ):
                continue

            # Look for opposing language.
            if not _contains_opposing_language(
                claim.statement,
                other_claim.statement,
            ):
                continue

            # Mark the other claim's source as contradicting this claim.
            for source_id in other_sources:
                claim.add_contradicting_source(source_id)

            claim.status = ClaimStatus.PARTIALLY_SUPPORTED
            claim.confidence = 0.5

    return investigation