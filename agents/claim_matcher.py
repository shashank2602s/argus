import re

from models.claims import Claim, ClaimStatus
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
    "according",
    "company",
    "companies",
    "organization",
    "organizations",
}


WORD_NORMALIZATIONS = {
    "artificial": "ai",
    "intelligence": "ai",
    "artificialintelligence": "ai",

    "cyberattack": "attack",
    "cyberattacks": "attack",
    "attacks": "attack",

    "threats": "threat",

    "risks": "risk",
    "risky": "risk",

    "enterprises": "enterprise",
    "organizations": "organization",
    "companies": "company",

    "increasing": "increase",
    "increased": "increase",
    "increases": "increase",

    "decreasing": "decrease",
    "decreased": "decrease",
    "decreases": "decrease",

    "growing": "growth",
    "grew": "growth",

    "attacked": "attack",
    "attacking": "attack",

    "vulnerable": "vulnerability",
    "vulnerabilities": "vulnerability",
}


KEYWORD_GROUPS = {
    "ai": {
        "ai",
        "artificial",
        "intelligence",
        "agentic",
        "machine",
        "learning",
    },

    "cybersecurity": {
        "cybersecurity",
        "security",
        "cyber",
        "threat",
        "attack",
    },

    "ransomware": {
        "ransomware",
        "extortion",
        "malware",
    },

    "deepfake": {
        "deepfake",
        "synthetic",
        "identity",
        "impersonation",
    },

    "governance": {
        "governance",
        "policy",
        "policies",
        "regulation",
        "regulatory",
    },

    "spending": {
        "spending",
        "budget",
        "investment",
        "invest",
        "expenditure",
    },
}


def _normalize_word(word: str) -> str:
    """
    Normalize common variations of important words.
    """

    word = word.lower()

    if word in WORD_NORMALIZATIONS:
        return WORD_NORMALIZATIONS[word]

    if len(word) > 5 and word.endswith("ies"):
        word = word[:-3] + "y"

    elif len(word) > 5 and word.endswith("ing"):
        word = word[:-3]

    elif len(word) > 4 and word.endswith("ed"):
        word = word[:-2]

    elif len(word) > 4 and word.endswith("s"):
        word = word[:-1]

    return word


def _meaningful_words(text: str) -> set[str]:
    """
    Return normalized content words from a claim.
    """

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower(),
    )

    normalized = set()

    for word in words:

        if len(word) < 4:
            continue

        if word in STOP_WORDS:
            continue

        normalized_word = _normalize_word(word)

        if len(normalized_word) >= 3:
            normalized.add(normalized_word)

    return normalized


def _topic_groups(words: set[str]) -> set[str]:
    """
    Identify high-level topics represented in a claim.
    """

    groups = set()

    for group_name, keywords in KEYWORD_GROUPS.items():

        if words & keywords:
            groups.add(group_name)

    return groups


def _word_similarity(
    words_a: set[str],
    words_b: set[str],
) -> float:
    """
    Calculate Jaccard similarity between normalized words.
    """

    if not words_a or not words_b:
        return 0.0

    intersection = words_a & words_b
    union = words_a | words_b

    return len(intersection) / len(union)


def _topic_similarity(
    words_a: set[str],
    words_b: set[str],
) -> float:
    """
    Measure similarity using broader cybersecurity topics.
    """

    topics_a = _topic_groups(words_a)
    topics_b = _topic_groups(words_b)

    if not topics_a or not topics_b:
        return 0.0

    intersection = topics_a & topics_b
    union = topics_a | topics_b

    return len(intersection) / len(union)


def _similarity(
    claim_a: Claim,
    claim_b: Claim,
) -> float:
    """
    Calculate combined claim similarity.
    """

    words_a = _meaningful_words(
        claim_a.statement
    )

    words_b = _meaningful_words(
        claim_b.statement
    )

    word_score = _word_similarity(
        words_a,
        words_b,
    )

    topic_score = _topic_similarity(
        words_a,
        words_b,
    )

    return (
        (word_score * 0.75)
        + (topic_score * 0.25)
    )


def _initialize_supporting_sources(
    claim: Claim,
) -> None:
    """
    Treat the source where the claim was originally found
    as supporting evidence.

    Additional independent sources are added later when
    matching claims are discovered.
    """

    for source_id in claim.source_ids:

        if source_id not in claim.supporting_sources:

            claim.supporting_sources.append(
                source_id
            )


def _merge_evidence(
    target: Claim,
    source: Claim,
) -> None:
    """
    Merge evidence from another matching claim into
    the canonical claim.
    """

    # --------------------------------------------------------
    # Preserve all sources associated with the claim
    # --------------------------------------------------------

    for source_id in source.source_ids:

        if source_id not in target.source_ids:

            target.source_ids.append(
                source_id
            )

    # --------------------------------------------------------
    # Add the independent source as supporting evidence
    # --------------------------------------------------------

    for source_id in source.source_ids:

        if source_id not in target.supporting_sources:

            target.supporting_sources.append(
                source_id
            )

    # --------------------------------------------------------
    # Preserve any existing supporting evidence
    # --------------------------------------------------------

    for source_id in source.supporting_sources:

        if source_id not in target.supporting_sources:

            target.supporting_sources.append(
                source_id
            )

    # --------------------------------------------------------
    # Preserve contradiction evidence
    # --------------------------------------------------------

    for source_id in source.contradicting_sources:

        if source_id not in target.contradicting_sources:

            target.contradicting_sources.append(
                source_id
            )


def _choose_canonical_claim(
    claim_a: Claim,
    claim_b: Claim,
) -> tuple[Claim, Claim]:
    """
    Choose which claim survives when two claims are matched.

    The longer statement is generally more informative.
    """

    if len(claim_a.statement) >= len(
        claim_b.statement
    ):
        return claim_a, claim_b

    return claim_b, claim_a


def match_claims(
    investigation: Investigation,
    threshold: float = 0.42,
) -> Investigation:
    """
    Match similar claims from independent sources.

    Every claim first receives its original source as
    supporting evidence.

    Similar claims from independent sources are then
    consolidated into a single canonical claim.

    This allows the verifier to distinguish between:

        1 source  -> 60%
        2 sources -> 75%
        3+ sources -> 90%

    Contradicting evidence is preserved separately.

    This implementation is deterministic and does not
    require an LLM or external API.
    """

    claims = investigation.claims

    if not claims:
        return investigation

    # --------------------------------------------------------
    # Step 1
    # Give every claim its original source as evidence.
    # --------------------------------------------------------

    for claim in claims:

        _initialize_supporting_sources(
            claim
        )

    if len(claims) < 2:
        return investigation

    # --------------------------------------------------------
    # Step 2
    # Find and consolidate similar claims.
    # --------------------------------------------------------

    active_claims = list(claims)

    changed = True

    while changed:

        changed = False

        for index in range(
            len(active_claims)
        ):

            base_claim = active_claims[index]

            for other_index in range(
                index + 1,
                len(active_claims),
            ):

                other_claim = (
                    active_claims[other_index]
                )

                base_sources = set(
                    base_claim.source_ids
                )

                other_sources = set(
                    other_claim.source_ids
                )

                # Never match claims originating
                # from the same source.
                if base_sources & other_sources:
                    continue

                similarity = _similarity(
                    base_claim,
                    other_claim,
                )

                if similarity < threshold:
                    continue

                canonical, duplicate = (
                    _choose_canonical_claim(
                        base_claim,
                        other_claim,
                    )
                )

                _merge_evidence(
                    canonical,
                    duplicate,
                )

                # Preserve contradiction information.
                if duplicate.contradicting_sources:

                    canonical.status = (
                        ClaimStatus.PARTIALLY_SUPPORTED
                    )

                    canonical.confidence = 0.50

                # Remove the duplicate claim.
                active_claims.remove(
                    duplicate
                )

                changed = True

                break

            if changed:
                break

    # --------------------------------------------------------
    # Step 3
    # Store the consolidated claims.
    # --------------------------------------------------------

    investigation.claims = active_claims

    return investigation