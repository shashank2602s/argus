import json

from models.claims import Claim, ClaimStatus
from models.sources import Source, SourceType


def main():
    # Create two example sources
    source1 = Source(
        id="src_001",
        url="https://example.com/company-report",
        title="Company Hiring Report",
        snippet="The company plans to hire 500 employees.",
        source_type=SourceType.PRIMARY,
        content="The company announced plans to hire 500 employees.",
        relevance_score=0.95,
    )

    source2 = Source(
        id="src_002",
        url="https://example.com/news-report",
        title="News Report",
        snippet="The company plans to hire 200 employees.",
        source_type=SourceType.NEWS,
        content="According to the report, the company plans to hire 200 employees.",
        relevance_score=0.88,
    )

    # Create a claim
    claim = Claim(
        id="claim_001",
        statement="The company plans to hire 500 employees.",
        evidence_excerpt="The company announced plans to hire 500 employees.",
        confidence=0.75,
        status=ClaimStatus.PARTIALLY_SUPPORTED,
    )

    # Link the sources to the claim
    claim.add_supporting_source(source1.id)
    claim.add_contradicting_source(source2.id)

    # Basic checks
    assert source1.domain == "example.com"
    assert source1.has_content is True

    assert source2.domain == "example.com"
    assert source2.has_content is True

    assert source1.id in claim.supporting_sources
    assert source2.id in claim.contradicting_sources

    assert source1.id in claim.source_ids
    assert source2.id in claim.source_ids

    assert claim.is_contested is True

    # Test Source serialization
    source1_dict = source1.to_dict()
    source1_json = json.dumps(source1_dict)
    source1_restored = Source.from_dict(json.loads(source1_json))

    assert source1_restored == source1

    # Test Claim serialization
    claim_dict = claim.to_dict()
    claim_json = json.dumps(claim_dict)
    claim_restored = Claim.from_dict(json.loads(claim_json))

    assert claim_restored == claim

    print("Source 1:")
    print(source1)
    print()

    print("Source 2:")
    print(source2)
    print()

    print("Claim:")
    print(claim)
    print()

    print("Claim JSON:")
    print(json.dumps(claim_dict, indent=2))
    print()

    print("All checks passed: models construct, link, and round-trip correctly.")


if __name__ == "__main__":
    main()