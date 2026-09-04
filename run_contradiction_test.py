from models.claims import Claim
from models.investigation import Investigation
from agents.contradiction_detector import detect_contradictions


def run_test(name, claims, expected_contradictions):
    investigation = Investigation(
        query=name,
        claims=claims,
    )

    result = detect_contradictions(investigation)

    contradiction_count = sum(
        1
        for claim in result.claims
        if claim.contradicting_sources
    )

    print(f"\n{name}")
    print("-" * 60)
    print(f"Expected claims with contradictions: {expected_contradictions}")
    print(f"Actual claims with contradictions:   {contradiction_count}")

    for claim in result.claims:
        print(f"\nClaim: {claim.statement}")
        print(f"Contradicting: {claim.contradicting_sources}")

    if contradiction_count == expected_contradictions:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")


# TEST 1: Opposing claims should be detected

claim_1 = Claim(
    id="claim-1",
    statement="Cybersecurity risks are increasing in 2026.",
    source_ids=["source-1"],
)

claim_2 = Claim(
    id="claim-2",
    statement="Cybersecurity risks are decreasing in 2026.",
    source_ids=["source-2"],
)

run_test(
    "TEST 1 - Contradicting claims",
    [claim_1, claim_2],
    expected_contradictions=2,
)


# TEST 2: Supporting claims should NOT be contradictions

claim_3 = Claim(
    id="claim-3",
    statement="AI-driven cyberattacks are increasing in 2026.",
    source_ids=["source-1"],
)

claim_4 = Claim(
    id="claim-4",
    statement="AI-powered cyberattacks are increasing this year.",
    source_ids=["source-2"],
)

run_test(
    "TEST 2 - Supporting claims",
    [claim_3, claim_4],
    expected_contradictions=0,
)


# TEST 3: Unrelated claims should NOT be contradictions

claim_5 = Claim(
    id="claim-5",
    statement="Cybersecurity risks are increasing in 2026.",
    source_ids=["source-1"],
)

claim_6 = Claim(
    id="claim-6",
    statement="Worldwide PC shipments grew by 9.1%.",
    source_ids=["source-2"],
)

run_test(
    "TEST 3 - Unrelated claims",
    [claim_5, claim_6],
    expected_contradictions=0,
)