from dataclasses import dataclass
from typing import List

from agents.reasoning import ReasoningError, ask_for_json


@dataclass
class InvestigationPlan:
    objective: str
    investigation_questions: List[str]
    search_queries: List[str]


SYSTEM_PROMPT = """
You are the planning component of ARGUS, an intelligence research system.

Your job is to turn a user's research question into a concrete investigation plan.

Return ONLY valid JSON with exactly these fields:

{
  "objective": "1-2 sentence description of what the investigation should determine",
  "investigation_questions": [
    "specific, checkable question",
    "specific, checkable question"
  ],
  "search_queries": [
    "concrete web search query",
    "concrete web search query"
  ]
}

Rules:
- Create 3-5 investigation questions.
- Create 3-6 search queries.
- Questions must be specific and answerable using evidence.
- Search queries should be concrete phrases suitable for a web search engine.
- Do not invent facts.
- Do not include markdown.
- Return JSON only.
"""


def create_plan(question: str) -> InvestigationPlan:
    """
    Turn a user's research question into a structured investigation plan.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    try:
        data = ask_for_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=question.strip(),
        )
    except ReasoningError:
        raise

    objective = data.get("objective")
    investigation_questions = data.get("investigation_questions")
    search_queries = data.get("search_queries")

    if not isinstance(objective, str) or not objective.strip():
        raise ReasoningError(
            "Planner response is missing a valid objective."
        )

    if (
        not isinstance(investigation_questions, list)
        or not 3 <= len(investigation_questions) <= 5
        or not all(isinstance(q, str) and q.strip() for q in investigation_questions)
    ):
        raise ReasoningError(
            "Planner response must contain 3-5 valid investigation questions."
        )

    if (
        not isinstance(search_queries, list)
        or not 3 <= len(search_queries) <= 6
        or not all(isinstance(q, str) and q.strip() for q in search_queries)
    ):
        raise ReasoningError(
            "Planner response must contain 3-6 valid search queries."
        )

    return InvestigationPlan(
        objective=objective.strip(),
        investigation_questions=[q.strip() for q in investigation_questions],
        search_queries=[q.strip() for q in search_queries],
    )