from dataclasses import dataclass, field
from typing import List

from models.claims import Claim
from models.sources import Source


@dataclass
class Investigation:
    query: str
    sources: List[Source] = field(default_factory=list)
    claims: List[Claim] = field(default_factory=list)