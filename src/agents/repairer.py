from pathlib import Path
from typing import Any

from src.agents.generator import generate_project
from src.models.schemas import ProjectPlan


def repair_project(
    plan: ProjectPlan,
    project_directory: Path | str,
    test_report: dict[str, Any],
    *,
    attempt: int,
) -> dict[str, Any]:
    """
    Repair a generated project by rebuilding its scaffold.

    This first repair-agent version is deterministic. It uses the
    original structured plan rather than an external LLM.
    """
    project_directory = Path(
        project_directory
    ).resolve()

    failed_checks = [
        check["name"]
        for check in test_report.get(
            "checks",
            [],
        )
        if check.get("status") == "failed"
    ]

    if not failed_checks:
        return {
            "status": "skipped",
            "attempt": attempt,
            "failed_checks": [],
            "actions": [
                "No failed checks required repair."
            ],
            "project_directory": str(
                project_directory
            ),
        }

    output_root = project_directory.parent

    repaired_directory = generate_project(
        plan,
        output_root=output_root,
        overwrite=True,
    )

    actions = [
        (
            "Regenerated the project scaffold from "
            "the original structured project plan."
        ),
        (
            "Replaced files associated with failed "
            "checks: "
            + ", ".join(failed_checks)
        ),
    ]

    return {
        "status": "completed",
        "attempt": attempt,
        "failed_checks": failed_checks,
        "actions": actions,
        "project_directory": str(
            repaired_directory.resolve()
        ),
    }