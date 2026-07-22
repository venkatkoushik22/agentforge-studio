import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import gradio as gr

from src.core.workflow import run_workflow


def _report_summary(
    result: dict[str, Any],
) -> dict[str, Any]:
    """Create a compact public-facing workflow report."""
    test_report = result.get("test_report") or {}
    security_report = result.get("security_report") or {}
    evaluation_report = result.get("evaluation_report") or {}

    return {
        "workflow_status": result.get("status"),
        "planner": result.get(
            "planner_used",
            "heuristic",
        ),
        "generated_project": str(
            result.get("project_directory", "")
        ),
        "tests": {
            "status": test_report.get("status"),
            "passed": test_report.get(
                "passed_checks",
                0,
            ),
            "failed": test_report.get(
                "failed_checks",
                0,
            ),
            "skipped": test_report.get(
                "skipped_checks",
                0,
            ),
        },
        "repair_attempts": result.get(
            "repair_attempts",
            0,
        ),
        "security": {
            "status": security_report.get("status"),
            "total_findings": security_report.get(
                "total_findings",
                0,
            ),
            "severity_counts": security_report.get(
                "severity_counts",
                {},
            ),
        },
        "evaluation": {
            "status": evaluation_report.get("status"),
            "score": evaluation_report.get(
                "overall_score",
            ),
            "passed_checks": evaluation_report.get(
                "passed_checks",
            ),
            "total_checks": evaluation_report.get(
                "total_checks",
            ),
        },
    }


def generate_application(
    requirement: str,
    minimum_score: float,
    max_repair_attempts: int,
) -> tuple[str, str, str | None]:
    """Generate, test, scan, evaluate, and package a project."""
    requirement = requirement.strip()

    if not requirement:
        error = {
            "workflow_status": "failed",
            "error": (
                "Enter an application requirement "
                "before starting generation."
            ),
        }

        return (
            "{}",
            json.dumps(error, indent=2),
            None,
        )

    temporary_root = Path(
        tempfile.mkdtemp(
            prefix="agentforge_",
        )
    )

    try:
        result = run_workflow(
            requirement,
            output_root=temporary_root,
            planner="heuristic",
            run_frontend_build=False,
            minimum_score=float(minimum_score),
            max_repair_attempts=int(
                max_repair_attempts
            ),
        )

        plan_json = json.dumps(
            result["plan"].to_dict(),
            indent=2,
        )

        summary_json = json.dumps(
            _report_summary(result),
            indent=2,
        )

        project_directory = Path(
            result["project_directory"]
        )

        archive_base = (
            temporary_root
            / f"{project_directory.name}-agentforge"
        )

        archive_path = shutil.make_archive(
            base_name=str(archive_base),
            format="zip",
            root_dir=project_directory,
        )

        return (
            plan_json,
            summary_json,
            archive_path,
        )

    except Exception as error:
        failure_report = {
            "workflow_status": "failed",
            "error_type": type(error).__name__,
            "error": str(error),
        }

        return (
            "{}",
            json.dumps(
                failure_report,
                indent=2,
            ),
            None,
        )


with gr.Blocks(
    title="AgentForge Studio",
) as demo:
    gr.Markdown(
        """
# 🛠️ AgentForge Studio

### Evaluation-first full-stack application generation

Describe an application and AgentForge will:

1. Create a structured project plan
2. Generate a React and FastAPI scaffold
3. Run automated tests
4. Repair validation failures
5. Scan the project for security risks
6. Evaluate project quality
7. Package the result as a downloadable ZIP

This public demo uses the free deterministic heuristic planner.
"""
    )

    requirement_input = gr.Textbox(
        label="Application requirement",
        placeholder=(
            "Build a React appointment booking platform "
            "using FastAPI and PostgreSQL with login, "
            "search, notifications, analytics, and "
            "admin roles."
        ),
        lines=6,
    )

    with gr.Row():
        minimum_score_input = gr.Slider(
            minimum=0,
            maximum=100,
            value=90,
            step=5,
            label="Minimum quality score",
        )

        repair_attempts_input = gr.Slider(
            minimum=0,
            maximum=3,
            value=1,
            step=1,
            label="Maximum repair attempts",
        )

    generate_button = gr.Button(
        "Generate Application",
        variant="primary",
    )

    with gr.Row():
        plan_output = gr.Code(
            label="Structured Project Plan",
            language="json",
        )

        report_output = gr.Code(
            label="Workflow Report",
            language="json",
        )

    download_output = gr.File(
        label="Download Generated Project",
    )

    generate_button.click(
        fn=generate_application,
        inputs=[
            requirement_input,
            minimum_score_input,
            repair_attempts_input,
        ],
        outputs=[
            plan_output,
            report_output,
            download_output,
        ],
    )

    gr.Markdown(
        """
---

### Current scope

The generated output is a development scaffold. Authentication,
payments, database persistence, deployment configuration, and
domain-specific business logic require further implementation.
"""
    )


if __name__ == "__main__":
    demo.queue(
        default_concurrency_limit=2
    ).launch()