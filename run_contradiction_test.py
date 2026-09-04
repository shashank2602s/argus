from agents.contradiction_detector import detect_contradictions
from models.claims import Claim, ClaimStatus
from models.investigation import Investigation
from models.sources import Source


def main():
    source_a = Source(
        id="source-1",
        url="https://example.com/source-a",
        title="Source A",
    )

    source_b = Source(
        id="source-2",
        url="https://example.com/source-b",
        title="Source B",
    )

    claim_a = Claim(
        id="claim-1",
        statement="Cybersecurity attacks increased significantly in 2026.",
        source_ids=["source-1"],
        supporting_sources=["source-1"],
        status=ClaimStatus.SUPPORTED,
    )

    claim_b = Claim(
        id="claim-2",
        statement="Cybersecurity attacks decreased significantly in 2026.",
        source_ids=["source-2"],
        supporting_sources=["source-2"],
        status=ClaimStatus.SUPPORTED,
    )

    investigation = Investigation(
        query="Did cybersecurity attacks increase or decrease in 2026?",
        sources=[source_a, source_b],
        claims=[claim_a, claim_b],
    )

    investigation = detect_contradictions(investigation)

    print("=== CONTRADICTION DETECTOR TEST ===")
    print()

    for claim in investigation.claims:
        print("Claim:", claim.statement)
        print("Status:", claim.status.value)
        print("Confidence:", claim.confidence)
        print("Supporting:", claim.supporting_sources)
        print("Contradicting:", claim.contradicting_sources)
        print("Contested:", claim.is_contested)
        print()


if __name__ == "__main__":
    main()