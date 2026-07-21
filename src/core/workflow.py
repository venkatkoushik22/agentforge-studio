import json
from pathlib import Path
from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from src.agents.generator import generate_project
from src.agents.planner import plan_project
from src.evaluation.evaluator import write_evaluation_report
from src.models.schemas import ProjectPlan
from src.security.scanner import write_report


class WorkflowState(TypedDict, total=False):
    requirement: str
    output_root: str | Path
    overwrite: bool
    skip_security_scan: bool
    skip_evaluation: bool
    minimum_score: float

    plan: ProjectPlan
    project_directory: Path
    security_report: dict[str, Any] | None
    evaluation_report: dict[str, Any] | None
    status: str


def _load_json(report_path: Path) -> dict[str, Any]:
    """Load a generated JSON report."""
    return json.loads(
        report_path.read_text(encoding="utf-8")
    )


def plan_node(state: WorkflowState) -> WorkflowState:
    """Convert the requirement into a structured project plan."""
    plan = plan_project(state["requirement"])

    return {
        "plan": plan,
        "status": "planned",
    }


def generate_node(state: WorkflowState) -> WorkflowState:
    """Generate the full-stack project scaffold."""
    project_directory = generate_project(
        state["plan"],
        output_root=state.get(
            "output_root",
            "generated_projects",
        ),
        overwrite=state.get("overwrite", False),
    )

    return {
        "project_directory": project_directory,
        "status": "generated",
    }


def security_node(state: WorkflowState) -> WorkflowState:
    """Run the security scanner unless explicitly skipped."""
    if state.get("skip_security_scan", False):
        return {
            "security_report": None,
            "status": "security_scan_skipped",
        }

    report_path = write_report(
        state["project_directory"]
    )

    return {
        "security_report": _load_json(report_path),
        "status": "security_scanned",
    }


def evaluation_node(state: WorkflowState) -> WorkflowState:
    """Evaluate the generated project's quality."""
    if state.get("skip_evaluation", False):
        return {
            "evaluation_report": None,
            "status": "evaluation_skipped",
        }

    report_path = write_evaluation_report(
        state["project_directory"]
    )

    return {
        "evaluation_report": _load_json(report_path),
        "status": "evaluated",
    }


def route_quality_gate(
    state: WorkflowState,
) -> Literal["passed", "failed"]:
    """Route the workflow based on its evaluation score."""
    if state.get("skip_evaluation", False):
        return "passed"

    evaluation = state.get("evaluation_report")

    if evaluation is None:
        return "failed"

    score = float(
        evaluation.get("overall_score", 0)
    )

    minimum_score = float(
        state.get("minimum_score", 80.0)
    )

    if score >= minimum_score:
        return "passed"

    return "failed"


def success_node(
    state: WorkflowState,
) -> WorkflowState:
    """Mark the workflow as successful."""
    return {"status": "passed"}


def failure_node(
    state: WorkflowState,
) -> WorkflowState:
    """Mark the workflow as failed."""
    return {"status": "failed"}


def build_workflow():
    """Build and compile the AgentForge workflow."""
    builder = StateGraph(WorkflowState)

    builder.add_node("plan", plan_node)
    builder.add_node("generate", generate_node)
    builder.add_node("security", security_node)
    builder.add_node("evaluate", evaluation_node)
    builder.add_node("success", success_node)
    builder.add_node("failure", failure_node)

    builder.add_edge(START, "plan")
    builder.add_edge("plan", "generate")
    builder.add_edge("generate", "security")
    builder.add_edge("security", "evaluate")

    builder.add_conditional_edges(
        "evaluate",
        route_quality_gate,
        {
            "passed": "success",
            "failed": "failure",
        },
    )

    builder.add_edge("success", END)
    builder.add_edge("failure", END)

    return builder.compile()


agentforge_workflow = build_workflow()


def run_workflow(
    requirement: str,
    *,
    output_root: str | Path = "generated_projects",
    overwrite: bool = False,
    skip_security_scan: bool = False,
    skip_evaluation: bool = False,
    minimum_score: float = 80.0,
) -> WorkflowState:
    """Run the complete AgentForge generation workflow."""
    if not requirement.strip():
        raise ValueError(
            "Project requirement cannot be empty."
        )

    if not 0 <= minimum_score <= 100:
        raise ValueError(
            "Minimum score must be between 0 and 100."
        )

    initial_state: WorkflowState = {
        "requirement": requirement,
        "output_root": output_root,
        "overwrite": overwrite,
        "skip_security_scan": skip_security_scan,
        "skip_evaluation": skip_evaluation,
        "minimum_score": minimum_score,
        "status": "started",
    }

    return agentforge_workflow.invoke(initial_state)