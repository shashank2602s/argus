from models.investigation import Investigation


def build_evidence_graph(
    investigation: Investigation,
) -> dict:
    """
    Build a graph representation of an investigation.

    Graph structure:

        Investigation Question
                ↓
             Claims
             ↙    ↘
        Sources   Sources

    Supporting and contradicting evidence are represented
    with different edge types.
    """

    nodes = []
    edges = []

    # Investigation node
    investigation_id = "investigation"

    nodes.append(
        {
            "id": investigation_id,
            "type": "investigation",
            "label": investigation.query,
        }
    )

    # Claim nodes
    for claim in investigation.claims:
        claim_id = f"claim:{claim.id}"

        nodes.append(
            {
                "id": claim_id,
                "type": "claim",
                "label": claim.statement,
                "status": claim.status.value,
                "confidence": claim.confidence,
                "contested": claim.is_contested,
            }
        )

        # Question → Claim
        edges.append(
            {
                "source": investigation_id,
                "target": claim_id,
                "type": "investigates",
            }
        )

    # Source nodes
    source_ids = set()

    for source in investigation.sources:
        source_id = f"source:{source.id}"

        if source.id not in source_ids:
            nodes.append(
                {
                    "id": source_id,
                    "type": "source",
                    "label": source.title or source.domain,
                    "domain": source.domain,
                    "url": source.url,
                }
            )

            source_ids.add(source.id)

    # Claim → Source relationships
    for claim in investigation.claims:
        claim_id = f"claim:{claim.id}"

        for source_id in claim.supporting_sources:
            edges.append(
                {
                    "source": claim_id,
                    "target": f"source:{source_id}",
                    "type": "supports",
                }
            )

        for source_id in claim.contradicting_sources:
            edges.append(
                {
                    "source": claim_id,
                    "target": f"source:{source_id}",
                    "type": "contradicts",
                }
            )

    return {
        "nodes": nodes,
        "edges": edges,
    }