from agents.investigator_loop import investigate_loop
from agents.state import InvestigationState


def main():
    state = InvestigationState(
        original_question="What are the major cybersecurity trends in 2026?"
    )

    state.objective = (
        "Identify major cybersecurity trends and supporting evidence."
    )

    state.investigation_questions = [
        "What major cybersecurity trends are emerging in 2026?",
        "What evidence supports these trends?",
    ]

    state.search_queries = [
        "cybersecurity trends 2026",
        "cybersecurity threats 2026",
        "AI cybersecurity trends 2026",
    ]

    print("=== ARGUS INVESTIGATOR LOOP ===")
    print("Question:", state.original_question)
    print("Search queries:", len(state.search_queries))
    print()

    print(
        "Running: Search -> Select -> Scrape -> "
        "Extract -> Verify -> Detect Contradictions -> "
        "Create Verification Tasks"
    )
    print()

    state = investigate_loop(state)

    print("=== RESULTS ===")
    print("Sources found:", len(state.sources))
    print(
        "Sources scraped:",
        state.usage_stats.get("sources_scraped", 0),
    )
    print("Claims extracted:", len(state.claims))
    print(
        "Contradictions detected:",
        state.usage_stats.get("contradictions_detected", 0),
    )
    print(
        "Verification tasks:",
        state.usage_stats.get("verification_tasks_created", 0),
    )
    print("Unresolved issues:", len(state.unresolved_questions))
    print()

    print("=== SOURCES ===")

    for i, source in enumerate(state.sources, 1):
        scraped = "scraped" if source.has_content else "not scraped"

        print(f"{i}. [{scraped}] {source.title}")
        print(f"   {source.url}")
        print()

    print("=== CLAIMS ===")

    for claim in state.claims[:10]:
        print(
            f"- {claim.status.value} | "
            f"confidence={claim.confidence} | "
            f"contested={claim.is_contested}"
        )
        print(f"  {claim.statement}")

        if claim.contradicting_sources:
            print(
                f"  Contradicting sources: "
                f"{claim.contradicting_sources}"
            )

        print()

    print("=== VERIFICATION TASKS ===")

    if state.verification_tasks:
        for task in state.verification_tasks:
            print("-", task)
    else:
        print("No verification tasks created.")

    print()
    print("=== USAGE ===")
    print(state.usage_stats)

    if state.unresolved_questions:
        print()
        print("=== UNRESOLVED ===")

        for issue in state.unresolved_questions:
            print("-", issue)


if __name__ == "__main__":
    main()