from models.investigation import Investigation


def create_verification_tasks(
    investigation: Investigation,
) -> list[str]:
    """
    Create follow-up verification tasks for contested claims.

    Each contested claim becomes a targeted research question that
    can be sent back through the search pipeline.
    """

    tasks = []

    for claim in investigation.claims:
        if not claim.is_contested:
            continue

        task = (
            "Verify this contested claim by finding additional "
            f"independent evidence: {claim.statement}"
        )

        if task not in tasks:
            tasks.append(task)

    return tasks