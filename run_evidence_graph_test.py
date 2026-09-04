from models.claims import Claim, ClaimStatus
from models.investigation import Investigation
from models.sources import Source
from agents.evidence_graph import build_evidence_graph


source_1 = Source(
    id="source-1",
    url="https://example.com/source-1",
    title="Cybersecurity Report",
    domain="example.com",
)

source_2 = Source(
    id="source-2",
    url="https://example.com/source-2",
    title="Security News",
    domain="example.com",
)

claim = Claim(
    id="claim-1",
    statement="Cybersecurity attacks increased significantly in 2026.",
    source_ids=["source-1", "source-2"],
    supporting_sources=["source-1"],
    contradicting_sources=["source-2"],
    confidence=0.5,
    status=ClaimStatus.PARTIALLY_SUPPORTED,
)

investigation = Investigation(
    query="Did cybersecurity attacks increase in 2026?",
    sources=[source_1, source_2],
    claims=[claim],
)


graph = build_evidence_graph(investigation)


print("\n=== NODES ===")

for node in graph["nodes"]:
    print(node)


print("\n=== EDGES ===")

for edge in graph["edges"]:
    print(edge)


print("\n=== SUMMARY ===")
print(f"Nodes: {len(graph['nodes'])}")
print(f"Edges: {len(graph['edges'])}")