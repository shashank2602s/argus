from agents.claim_matcher import match_claims
from models.claims import Claim, ClaimStatus
from models.investigation import Investigation
from models.sources import Source


def main():
    source_a = Source(
        id="source-1",
        url="https://example.com/source-a",
        title="Cybersecurity Report A",
    )

    source_b = Source(
        id="source-2",
        url="https://example.com/source-b",
        title="Cybersecurity Report B",
    )

    claim_a = Claim(
        id="claim-1",
        statement=(
            "AI enabled cybersecurity attacks increased significantly "
            "in 2026 according to a recent industry report."
        ),
        source_ids=["source-1"],
        supporting_sources=["source-1"],
        status=ClaimStatus.SUPPORTED,
    )

    claim_b = Claim(
        id="claim-2",
        statement=(
            "Cybersecurity attacks using artificial intelligence "
            "increased significantly during 2026 according to researchers."
        ),
        source_ids=["source-2"],
        supporting_sources=["source-2"],
        status=ClaimStatus.SUPPORTED,
    )

    investigation = Investigation(
        query="Did AI enabled cybersecurity attacks increase in 2026?",
        sources=[source_a, source_b],
        claims=[claim_a, claim_b],
    )

    investigation = match_claims(investigation)

    print("=== CLAIM MATCHER TEST ===")
    print()

    for claim in investigation.claims:
        print("Claim:", claim.statement)
        print("Sources:", claim.source_ids)
        print("Supporting:", claim.supporting_sources)
        print()


if __name__ == "__main__":
    main()