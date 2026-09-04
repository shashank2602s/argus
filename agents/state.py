from dataclasses import dataclass, field
from typing import List, Dict, Any

from models.claims import Claim
from models.sources import Source


@dataclass
class InvestigationState:
    """
    Shared state that moves through the ARGUS investigation pipeline.
    """

    original_question: str

    objective: str = ""

    investigation_questions: List[str] = field(default_factory=list)

    search_queries: List[str] = field(default_factory=list)

    sources: List[Source] = field(default_factory=list)

    claims: List[Claim] = field(default_factory=list)

    contradictions: List[str] = field(default_factory=list)

    unresolved_questions: List[str] = field(default_factory=list)

    verification_tasks: List[str] = field(default_factory=list)

    timeline_events: List[Dict[str, Any]] = field(default_factory=list)

    final_report: str = ""

    confidence: float = 0.0

    usage_stats: Dict[str, Any] = field(default_factory=dict)

    def add_source(self, source: Source) -> None:
        """Add a source if the URL has not already been added."""

        existing_urls = {item.url for item in self.sources}

        if source.url not in existing_urls:
            self.sources.append(source)

    def add_claim(self, claim: Claim) -> None:
        """Add a claim if it has not already been added."""

        existing_ids = {item.id for item in self.claims}

        if claim.id not in existing_ids:
            self.claims.append(claim)

    def add_verification_task(self, task: str) -> None:
        """Add a verification task if it does not already exist."""

        if task not in self.verification_tasks:
            self.verification_tasks.append(task)

    def summary(self) -> Dict[str, Any]:
        """Return a compact snapshot of investigation progress."""

        scraped_sources = sum(
            1
            for source in self.sources
            if source.has_content
        )

        return {
            "question": self.original_question,
            "sources": len(self.sources),
            "scraped_sources": scraped_sources,
            "claims": len(self.claims),
            "contradictions": len(self.contradictions),
            "unresolved_questions": len(self.unresolved_questions),
            "verification_tasks": len(self.verification_tasks),
            "confidence": self.confidence,
        }