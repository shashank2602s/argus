from agents.investigator_loop import investigate_loop
from agents.state import InvestigationState


QUERY = "What are the major cybersecurity trends in 2026?"


print("=" * 70)
print("ARGUS FULL PIPELINE TEST")
print("=" * 70)
print(f"\nQuery: {QUERY}\n")


state = InvestigationState(
    original_question=QUERY,
    search_queries=[QUERY],
)


try:
    result = investigate_loop(state)

    print("\n" + "=" * 70)
    print("PIPELINE RESULTS")
    print("=" * 70)

    print(f"\nSources found:              {len(result.sources)}")
    print(
        f"Sources scraped:            "
        f"{sum(1 for source in result.sources if source.has_content)}"
    )
    print(f"Claims extracted:            {len(result.claims)}")
    print(f"Contradictions detected:     {len(result.contradictions)}")
    print(f"Verification tasks:          {len(result.verification_tasks)}")

    print("\n" + "-" * 70)
    print("CLAIMS")
    print("-" * 70)

    for claim in result.claims:
        print(f"\nClaim: {claim.statement}")
        print(f"Status: {claim.status.value}")
        print(f"Confidence: {claim.confidence}")
        print(f"Supporting: {claim.supporting_sources}")
        print(f"Contradicting: {claim.contradicting_sources}")

    print("\n" + "-" * 70)
    print("USAGE STATS")
    print("-" * 70)

    for key, value in result.usage_stats.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 70)
    print("FULL PIPELINE TEST COMPLETED")
    print("=" * 70)

except Exception as exc:
    print("\n" + "=" * 70)
    print("PIPELINE TEST FAILED")
    print("=" * 70)
    print(f"\nError: {exc}")
    raise