from collections import Counter

from models.claims import Claim
from models.investigation import Investigation


def verify_claims(investigation: Investigation) -> Investigation:
    """
    Verify claims by checking how many sources support each claim.

    This first version uses source agreement as a basic confidence signal.
    """

    if not investigation.claims:
        return investigation

    source_counts = Counter()

    for claim in investigation.claims:
        for url in claim.source_urls:
            source_counts[url] += 1

    for claim in investigation.claims:
        if not claim.source_urls:
            claim.confidence = 0.0
            continue

        supporting_sources = len(set(claim.source_urls))

        if supporting_sources >= 3:
            claim.confidence = 0.9
        elif supporting_sources == 2:
            claim.confidence = 0.7
        else:
            claim.confidence = 0.4

    return investigation