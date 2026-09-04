from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import urlparse


class SourceType(str, Enum):
    PRIMARY = "primary"
    OFFICIAL = "official"
    NEWS = "news"
    SECONDARY = "secondary"
    UNKNOWN = "unknown"


@dataclass
class Source:
    id: str
    url: str
    title: str
    domain: str = ""
    snippet: str = ""
    retrieved_at: Optional[str] = None
    publication_date: Optional[str] = None
    source_type: SourceType = SourceType.UNKNOWN
    content: str = ""
    relevance_score: float = 0.0

    def __post_init__(self):
        if not self.domain:
            self.domain = urlparse(self.url).netloc

    @property
    def has_content(self) -> bool:
        return bool(self.content.strip())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "domain": self.domain,
            "snippet": self.snippet,
            "retrieved_at": self.retrieved_at,
            "publication_date": self.publication_date,
            "source_type": self.source_type.value,
            "content": self.content,
            "relevance_score": self.relevance_score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Source":
        return cls(
            id=data["id"],
            url=data["url"],
            title=data["title"],
            domain=data.get("domain", ""),
            snippet=data.get("snippet", ""),
            retrieved_at=data.get("retrieved_at"),
            publication_date=data.get("publication_date"),
            source_type=SourceType(
                data.get("source_type", SourceType.UNKNOWN.value)
            ),
            content=data.get("content", ""),
            relevance_score=float(data.get("relevance_score", 0.0)),
        )