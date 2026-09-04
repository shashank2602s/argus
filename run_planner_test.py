import sys

from agents.planner import create_plan
from agents.reasoning import ReasoningError


def main():
    question = " ".join(sys.argv[1:]).strip()

    if not question:
        question = (
            "Is Acme Corp rapidly expanding its cybersecurity operations?"
        )

    print(f"Question: {question}\n")

    try:
        plan = create_plan(question)
    except ReasoningError as exc:
        print(f"REASONING ERROR: {exc}")
        return
    except Exception as exc:
        print(f"ERROR: {exc}")
        return

    print("Objective:")
    print(f"  {plan.objective}\n")

    print("Investigation questions:")
    for index, item in enumerate(plan.investigation_questions, start=1):
        print(f"  {index}. {item}")

    print("\nSearch queries:")
    for index, item in enumerate(plan.search_queries, start=1):
        print(f"  {index}. {item}")


if __name__ == "__main__":
    main()