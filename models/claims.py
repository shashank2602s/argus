from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ClaimStatus(str, Enum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    CONTRADICTED = "contradicted"
    UNVERIFIED = "unverified"


@dataclass
class Claim:
    id: str
    statement: str
    source_ids: List[str] = field(default_factory=list)
    evidence_excerpt: str = ""
    date: str = ""
    entities: List[str] = field(default_factory=list)
    supporting_sources: List[str] = field(default_factory=list)
    contradicting_sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    status: ClaimStatus = ClaimStatus.UNVERIFIED

    def add_supporting_source(self, source_id: str) -> None:
        if source_id not in self.supporting_sources:
            self.supporting_sources.append(source_id)

        if source_id not in self.source_ids:
            self.source_ids.append(source_id)

    def add_contradicting_source(self, source_id: str) -> None:
        if source_id not in self.contradicting_sources:
            self.contradicting_sources.append(source_id)

        if source_id not in self.source_ids:
            self.source_ids.append(source_id)

    @property
    def is_contested(self) -> bool:
        return bool(
            self.supporting_sources
            and self.contradicting_sources
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "statement": self.statement,
            "source_ids": self.source_ids,
            "evidence_excerpt": self.evidence_excerpt,
            "date": self.date,
            "entities": self.entities,
            "supporting_sources": self.supporting_sources,
            "contradicting_sources": self.contradicting_sources,
            "confidence": self.confidence,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Claim":
        return cls(
            id=data["id"],
            statement=data["statement"],
            source_ids=list(data.get("source_ids", [])),
            evidence_excerpt=data.get("evidence_excerpt", ""),
            date=data.get("date", ""),
            entities=list(data.get("entities", [])),
            supporting_sources=list(
                data.get("supporting_sources", [])
            ),
            contradicting_sources=list(
                data.get("contradicting_sources", [])
            ),
            confidence=float(data.get("confidence", 0.0)),
            status=ClaimStatus(
                data.get("status", ClaimStatus.UNVERIFIED.value)
            ),
        )