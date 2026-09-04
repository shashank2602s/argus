from models.claims import ClaimStatus
from models.investigation import Investigation


def verify_claims(investigation: Investigation) -> Investigation:
    """
    Verify claims using supporting and contradicting source counts.

    This first version uses source agreement as a basic confidence signal.
    """

    for claim in investigation.claims:
        supporting = len(set(claim.supporting_sources))
        contradicting = len(set(claim.contradicting_sources))

        if supporting == 0 and contradicting == 0:
            claim.confidence = 0.0
            claim.status = ClaimStatus.UNVERIFIED

        elif contradicting > supporting:
            claim.confidence = 0.3
            claim.status = ClaimStatus.CONTRADICTED

        elif supporting > 0 and contradicting > 0:
            claim.confidence = 0.5
            claim.status = ClaimStatus.PARTIALLY_SUPPORTED

        elif supporting >= 3:
            claim.confidence = 0.9
            claim.status = ClaimStatus.SUPPORTED

        elif supporting == 2:
            claim.confidence = 0.7
            claim.status = ClaimStatus.SUPPORTED

        else:
            claim.confidence = 0.4
            claim.status = ClaimStatus.SUPPORTED

    return investigation