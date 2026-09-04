from models.claims import Claim, ClaimStatus
from models.investigation import Investigation
from agents.verifier import verify_claims


def run_test(name, claim, expected_status, expected_confidence):
    investigation = Investigation(
        query=name,
        claims=[claim],
    )

    result = verify_claims(investigation)
    verified_claim = result.claims[0]

    print(f"\n{name}")
    print("-" * 60)
    print(f"Expected status:     {expected_status.value}")
    print(f"Actual status:       {verified_claim.status.value}")
    print(f"Expected confidence: {expected_confidence}")
    print(f"Actual confidence:   {verified_claim.confidence}")

    if (
        verified_claim.status == expected_status
        and verified_claim.confidence == expected_confidence
    ):
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")


# TEST 1: One supporting source -> 60%

claim_1 = Claim(
    id="claim-1",
    statement="AI cyberattacks are increasing.",
    supporting_sources=["source-1"],
)

run_test(
    "TEST 1 - One supporting source",
    claim_1,
    ClaimStatus.SUPPORTED,
    0.60,
)


# TEST 2: Two supporting sources -> 75%

claim_2 = Claim(
    id="claim-2",
    statement="AI cyberattacks are increasing.",
    supporting_sources=["source-1", "source-2"],
)

run_test(
    "TEST 2 - Two supporting sources",
    claim_2,
    ClaimStatus.SUPPORTED,
    0.75,
)


# TEST 3: Three supporting sources -> 90%

claim_3 = Claim(
    id="claim-3",
    statement="AI cyberattacks are increasing.",
    supporting_sources=[
        "source-1",
        "source-2",
        "source-3",
    ],
)

run_test(
    "TEST 3 - Three supporting sources",
    claim_3,
    ClaimStatus.SUPPORTED,
    0.90,
)


# TEST 4: No evidence -> 0%

claim_4 = Claim(
    id="claim-4",
    statement="AI cyberattacks are increasing.",
)

run_test(
    "TEST 4 - No supporting evidence",
    claim_4,
    ClaimStatus.UNVERIFIED,
    0.0,
)


# TEST 5: Contradicting evidence takes priority

claim_5 = Claim(
    id="claim-5",
    statement="AI cyberattacks are increasing.",
    supporting_sources=["source-1"],
    contradicting_sources=[
        "source-2",
        "source-3",
    ],
)

run_test(
    "TEST 5 - Contradicting evidence",
    claim_5,
    ClaimStatus.CONTRADICTED,
    0.30,
)