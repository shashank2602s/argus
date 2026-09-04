from models.claims import ClaimStatus
from models.investigation import Investigation


def verify_claims(
    investigation: Investigation,
) -> Investigation:
    """
    Verify claims using independent supporting and
    contradicting source evidence.

    Confidence levels:
        0 sources  -> UNVERIFIED
        1 source   -> SUPPORTED, 60%
        2 sources  -> SUPPORTED, 75%
        3+ sources -> SUPPORTED, 90%

    Contradicting evidence takes priority over
    supporting evidence.
    """

    for claim in investigation.claims:

        supporting = len(
            set(claim.supporting_sources)
        )

        contradicting = len(
            set(claim.contradicting_sources)
        )

        # --------------------------------------------------------
        # No evidence
        # --------------------------------------------------------

        if supporting == 0 and contradicting == 0:

            claim.confidence = 0.0
            claim.status = ClaimStatus.UNVERIFIED

        # --------------------------------------------------------
        # More contradicting evidence than supporting evidence
        # --------------------------------------------------------

        elif contradicting > supporting:

            claim.status = ClaimStatus.CONTRADICTED

            if supporting == 0:
                claim.confidence = 0.15
            else:
                claim.confidence = 0.30

        # --------------------------------------------------------
        # Both supporting and contradicting evidence
        # --------------------------------------------------------

        elif supporting > 0 and contradicting > 0:

            claim.status = ClaimStatus.PARTIALLY_SUPPORTED

            if supporting > contradicting:
                claim.confidence = 0.65

            elif supporting == contradicting:
                claim.confidence = 0.50

            else:
                claim.confidence = 0.35

        # --------------------------------------------------------
        # Three or more supporting sources
        # --------------------------------------------------------

        elif supporting >= 3:

            claim.confidence = 0.90
            claim.status = ClaimStatus.SUPPORTED

        # --------------------------------------------------------
        # Two supporting sources
        # --------------------------------------------------------

        elif supporting == 2:

            claim.confidence = 0.75
            claim.status = ClaimStatus.SUPPORTED

        # --------------------------------------------------------
        # One supporting source
        # --------------------------------------------------------

        elif supporting == 1:

            claim.confidence = 0.60
            claim.status = ClaimStatus.SUPPORTED

    return investigation