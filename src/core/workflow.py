import json
from pathlib import Path
from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from src.agents.generator import generate_project
from src.agents.planner import plan_project
from src.agents.repairer import repair_project
from src.agents.tester import write_test_report
from src.evaluation.evaluator import (
    write_evaluation_report,
)
from src.models.schemas import ProjectPlan
from src.security.scanner import write_report


PlannerType = Literal[
    "heuristic",
    "llm",
]


class WorkflowState(TypedDict, total=False):
    requirement: str
    output_root: str | Path
    overwrite: bool

    planner: PlannerType
    llm_model: str | None
    planner_used: str

    skip_security_scan: bool
    skip_evaluation: bool
    run_frontend_build: bool
    minimum_score: float

    repair_attempts: int
    max_repair_attempts: int
    repair_history: list[dict[str, Any]]

    plan: ProjectPlan
    project_directory: Path

    test_report: dict[str, Any] | None
    security_report: dict[str, Any] | None
    evaluation_report: dict[str, Any] | None

    status: str


def _load_json(
    path: Path,
) -> dict[str, Any]:
    """Load a JSON report from disk."""
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def plan_node(
    state: WorkflowState,
) -> WorkflowState:
    """Create a structured project plan."""
    planner = state.get(
        "planner",
        "heuristic",
    )

    if planner == "llm":
        try:
            from src.agents.llm_planner import (
                plan_project_with_llm,
            )
        except ImportError as error:
            raise RuntimeError(
                "LLM planning dependencies are not "
                "installed. Run: "
                "py -m pip install -r "
                "requirements-llm.txt"
            ) from error

        plan = plan_project_with_llm(
            state["requirement"],
            model=state.get(
                "llm_model"
            ),
        )
    else:
        plan = plan_project(
            state["requirement"]
        )

    return {
        "plan": plan,
        "planner_used": planner,
        "status": "planned",
    }


def generate_node(
    state: WorkflowState,
) -> WorkflowState:
    """Generate the full-stack scaffold."""
    project_directory = generate_project(
        state["plan"],
        output_root=state.get(
            "output_root",
            "generated_projects",
        ),
        overwrite=state.get(
            "overwrite",
            False,
        ),
    )

    return {
        "project_directory": (
            project_directory
        ),
        "status": "generated",
    }


def test_node(
    state: WorkflowState,
) -> WorkflowState:
    """Run automated generated-project tests."""
    report_path = write_test_report(
        state["project_directory"],
        run_frontend_build=state.get(
            "run_frontend_build",
            True,
        ),
    )

    return {
        "test_report": _load_json(
            report_path
        ),
        "status": "tested",
    }


def route_after_test(
    state: WorkflowState,
) -> Literal[
    "security",
    "repair",
    "failure",
]:
    """Route based on the automated test result."""
    report = state.get(
        "test_report"
    )

    if (
        report is not None
        and report.get("status") == "passed"
    ):
        return "security"

    attempts = state.get(
        "repair_attempts",
        0,
    )

    maximum_attempts = state.get(
        "max_repair_attempts",
        1,
    )

    if attempts < maximum_attempts:
        return "repair"

    return "failure"


def repair_node(
    state: WorkflowState,
) -> WorkflowState:
    """Repair the project before retesting."""
    current_attempts = state.get(
        "repair_attempts",
        0,
    )

    next_attempt = (
        current_attempts + 1
    )

    test_report = state.get(
        "test_report"
    )

    if test_report is None:
        raise RuntimeError(
            "Repair was requested without "
            "a test report."
        )

    result = repair_project(
        state["plan"],
        state["project_directory"],
        test_report,
        attempt=next_attempt,
    )

    repair_history = [
        *state.get(
            "repair_history",
            [],
        ),
        result,
    ]

    return {
        "project_directory": Path(
            result["project_directory"]
        ),
        "repair_attempts": next_attempt,
        "repair_history": repair_history,
        "status": "repaired",
    }


def security_node(
    state: WorkflowState,
) -> WorkflowState:
    """Run the generated-code security scanner."""
    if state.get(
        "skip_security_scan",
        False,
    ):
        return {
            "security_report": None,
            "status": (
                "security_scan_skipped"
            ),
        }

    report_path = write_report(
        state["project_directory"]
    )

    return {
        "security_report": _load_json(
            report_path
        ),
        "status": "security_scanned",
    }


def evaluation_node(
    state: WorkflowState,
) -> WorkflowState:
    """Evaluate generated-project quality."""
    if state.get(
        "skip_evaluation",
        False,
    ):
        return {
            "evaluation_report": None,
            "status": (
                "evaluation_skipped"
            ),
        }

    report_path = (
        write_evaluation_report(
            state["project_directory"]
        )
    )

    return {
        "evaluation_report": _load_json(
            report_path
        ),
        "status": "evaluated",
    }


def route_quality_gate(
    state: WorkflowState,
) -> Literal[
    "passed",
    "failed",
]:
    """Route according to evaluation score."""
    if state.get(
        "skip_evaluation",
        False,
    ):
        return "passed"

    evaluation = state.get(
        "evaluation_report"
    )

    if evaluation is None:
        return "failed"

    score = float(
        evaluation.get(
            "overall_score",
            0,
        )
    )

    minimum_score = float(
        state.get(
            "minimum_score",
            80.0,
        )
    )

    if score >= minimum_score:
        return "passed"

    return "failed"


def success_node(
    state: WorkflowState,
) -> WorkflowState:
    """Mark the workflow as successful."""
    return {
        "status": "passed"
    }


def failure_node(
    state: WorkflowState,
) -> WorkflowState:
    """Mark the workflow as failed."""
    return {
        "status": "failed"
    }


def build_workflow():
    """Build and compile AgentForge's graph."""
    builder = StateGraph(
        WorkflowState
    )

    builder.add_node(
        "plan",
        plan_node,
    )

    builder.add_node(
        "generate",
        generate_node,
    )

    builder.add_node(
        "test",
        test_node,
    )

    builder.add_node(
        "repair",
        repair_node,
    )

    builder.add_node(
        "security",
        security_node,
    )

    builder.add_node(
        "evaluate",
        evaluation_node,
    )

    builder.add_node(
        "success",
        success_node,
    )

    builder.add_node(
        "failure",
        failure_node,
    )

    builder.add_edge(
        START,
        "plan",
    )

    builder.add_edge(
        "plan",
        "generate",
    )

    builder.add_edge(
        "generate",
        "test",
    )

    builder.add_conditional_edges(
        "test",
        route_after_test,
        {
            "security": "security",
            "repair": "repair",
            "failure": "failure",
        },
    )

    builder.add_edge(
        "repair",
        "test",
    )

    builder.add_edge(
        "security",
        "evaluate",
    )

    builder.add_conditional_edges(
        "evaluate",
        route_quality_gate,
        {
            "passed": "success",
            "failed": "failure",
        },
    )

    builder.add_edge(
        "success",
        END,
    )

    builder.add_edge(
        "failure",
        END,
    )

    return builder.compile()


agentforge_workflow = (
    build_workflow()
)


def run_workflow(
    requirement: str,
    *,
    output_root: str | Path = (
        "generated_projects"
    ),
    overwrite: bool = False,
    planner: PlannerType = "heuristic",
    llm_model: str | None = None,
    skip_security_scan: bool = False,
    skip_evaluation: bool = False,
    run_frontend_build: bool = True,
    minimum_score: float = 80.0,
    max_repair_attempts: int = 1,
) -> WorkflowState:
    """Run the complete AgentForge workflow."""
    requirement = requirement.strip()

    if not requirement:
        raise ValueError(
            "Project requirement cannot "
            "be empty."
        )

    if not 0 <= minimum_score <= 100:
        raise ValueError(
            "Minimum score must be "
            "between 0 and 100."
        )

    if planner not in {
        "heuristic",
        "llm",
    }:
        raise ValueError(
            "Planner must be either "
            "'heuristic' or 'llm'."
        )

    if not 0 <= max_repair_attempts <= 3:
        raise ValueError(
            "Maximum repair attempts must "
            "be between 0 and 3."
        )

    initial_state: WorkflowState = {
        "requirement": requirement,
        "output_root": output_root,
        "overwrite": overwrite,
        "planner": planner,
        "llm_model": llm_model,
        "skip_security_scan": (
            skip_security_scan
        ),
        "skip_evaluation": (
            skip_evaluation
        ),
        "run_frontend_build": (
            run_frontend_build
        ),
        "minimum_score": minimum_score,
        "repair_attempts": 0,
        "max_repair_attempts": (
            max_repair_attempts
        ),
        "repair_history": [],
        "status": "started",
    }

    return agentforge_workflow.invoke(
        initial_state
    )