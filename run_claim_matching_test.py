from models.claims import Claim
from models.investigation import Investigation
from agents.claim_matcher import match_claims


def run_test(name, claims, expected_count):
    investigation = Investigation(
        query=name,
        claims=claims,
    )

    result = match_claims(investigation)

    actual_count = len(result.claims)

    print(f"\n{name}")
    print("-" * 60)
    print(f"Expected claims after matching: {expected_count}")
    print(f"Actual claims after matching:   {actual_count}")

    for claim in result.claims:
        print(f"\nClaim: {claim.statement}")
        print(f"Supporting: {claim.supporting_sources}")
        print(f"Contradicting: {claim.contradicting_sources}")
        print(f"Status: {claim.status.value}")
        print(f"Confidence: {claim.confidence}")

    if actual_count == expected_count:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")


# TEST 1: Similar claims should MATCH

claim_1 = Claim(
    id="claim-1",
    statement="AI-driven cyberattacks are increasing in 2026.",
    source_ids=["source-1"],
)

claim_2 = Claim(
    id="claim-2",
    statement="Cyberattacks powered by artificial intelligence are increasing this year.",
    source_ids=["source-2"],
)

run_test(
    "TEST 1 - Similar claims",
    [claim_1, claim_2],
    expected_count=1,
)


# TEST 2: Unrelated claims should NOT MATCH

claim_3 = Claim(
    id="claim-3",
    statement="AI-driven cyberattacks are increasing in 2026.",
    source_ids=["source-1"],
)

claim_4 = Claim(
    id="claim-4",
    statement="Worldwide PC shipments grew by 9.1%.",
    source_ids=["source-2"],
)

run_test(
    "TEST 2 - Unrelated claims",
    [claim_3, claim_4],
    expected_count=2,
)


# TEST 3: Same-source claims should NOT count as independent

claim_5 = Claim(
    id="claim-5",
    statement="AI-driven cyberattacks are increasing in 2026.",
    source_ids=["source-1"],
)

claim_6 = Claim(
    id="claim-6",
    statement="Cyberattacks powered by artificial intelligence are increasing this year.",
    source_ids=["source-1"],
)

run_test(
    "TEST 3 - Same source",
    [claim_5, claim_6],
    expected_count=2,
)


# TEST 4: Three independent matching claims

claim_7 = Claim(
    id="claim-7",
    statement="AI-driven cyberattacks are increasing in 2026.",
    source_ids=["source-1"],
)

claim_8 = Claim(
    id="claim-8",
    statement="Cyberattacks powered by artificial intelligence are increasing this year.",
    source_ids=["source-2"],
)

claim_9 = Claim(
    id="claim-9",
    statement="Artificial intelligence is driving an increase in cyberattacks during 2026.",
    source_ids=["source-3"],
)

run_test(
    "TEST 4 - Three independent sources",
    [claim_7, claim_8, claim_9],
    expected_count=1,
)