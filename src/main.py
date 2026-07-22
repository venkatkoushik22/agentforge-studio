import argparse
import json
from pathlib import Path
from typing import Any

from src.agents.planner import plan_project
from src.core.workflow import run_workflow


def save_plan(
    project_name: str,
    plan_data: dict[str, Any],
) -> Path:
    """Save a plan without generating an application."""
    project_directory = (
        Path("generated_projects") / project_name
    )

    project_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        project_directory / "project_plan.json"
    )

    output_file.write_text(
        json.dumps(plan_data, indent=2),
        encoding="utf-8",
    )

    return output_file


def create_plan_only(
    requirement: str,
    planner: str,
    llm_model: str | None,
):
    """Create a plan without running generation."""
    if planner == "llm":
        try:
            from src.agents.llm_planner import (
                plan_project_with_llm,
            )
        except ImportError as error:
            raise RuntimeError(
                "LLM dependencies are not installed. "
                "Run: py -m pip install -r "
                "requirements-llm.txt"
            ) from error

        return plan_project_with_llm(
            requirement,
            model=llm_model,
        )

    return plan_project(requirement)


def print_test_summary(
    report: dict[str, Any] | None,
) -> None:
    """Print generated-project test results."""
    print("\nAutomated tests")
    print("---------------")

    if report is None:
        print("Status: unavailable")
        return

    print(f"Status: {report['status']}")
    print(
        f"Passed: {report['passed_checks']}"
    )
    print(
        f"Failed: {report['failed_checks']}"
    )
    print(
        f"Skipped: {report['skipped_checks']}"
    )
    print(
        f"Total: {report['total_checks']}"
    )

    for check in report["checks"]:
        marker = check["status"].upper()

        print(
            f"[{marker}] {check['name']}: "
            f"{check['details']} "
            f"({check['duration_ms']} ms)"
        )


def print_repair_summary(
    attempts: int,
    history: list[dict[str, Any]],
) -> None:
    """Print actions taken by the repair agent."""
    print("\nRepair agent")
    print("------------")
    print(f"Attempts used: {attempts}")

    if not history:
        print(
            "No repairs were needed. "
            "The generated project passed its tests."
        )
        return

    for repair in history:
        print(
            f"\nAttempt {repair['attempt']}: "
            f"{repair['status']}"
        )

        failed_checks = repair.get(
            "failed_checks",
            [],
        )

        if failed_checks:
            print(
                "Failed checks: "
                + ", ".join(failed_checks)
            )

        for action in repair.get(
            "actions",
            [],
        ):
            print(f"- {action}")


def print_security_summary(
    report: dict[str, Any] | None,
) -> None:
    """Print generated-code security results."""
    print("\nSecurity scan")
    print("-------------")

    if report is None:
        print("Status: skipped")
        return

    severity_counts = report[
        "severity_counts"
    ]

    print(f"Status: {report['status']}")
    print(
        "Total findings: "
        f"{report['total_findings']}"
    )
    print(
        "Critical: "
        f"{severity_counts['CRITICAL']}"
    )
    print(
        f"High: {severity_counts['HIGH']}"
    )
    print(
        f"Medium: {severity_counts['MEDIUM']}"
    )
    print(
        f"Low: {severity_counts['LOW']}"
    )


def print_evaluation_summary(
    report: dict[str, Any] | None,
) -> None:
    """Print generated-project evaluation results."""
    print("\nQuality evaluation")
    print("------------------")

    if report is None:
        print("Status: skipped")
        return

    print(f"Status: {report['status']}")
    print(
        f"Score: {report['overall_score']}%"
    )
    print(
        "Checks passed: "
        f"{report['passed_checks']}/"
        f"{report['total_checks']}"
    )

    for check in report["checks"]:
        marker = (
            "PASS"
            if check["passed"]
            else "FAIL"
        )

        print(
            f"[{marker}] {check['name']}: "
            f"{check['details']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Plan, generate, test, repair, scan, and "
            "evaluate applications through AgentForge."
        )
    )

    parser.add_argument(
        "requirement",
        nargs="?",
        help="Natural-language application description.",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save only the structured project plan.",
    )

    parser.add_argument(
        "--generate",
        action="store_true",
        help="Run the complete generation workflow.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing generated project.",
    )

    parser.add_argument(
        "--planner",
        choices=[
            "heuristic",
            "llm",
        ],
        default="heuristic",
        help=(
            "Planning method. The heuristic planner "
            "is free and is used by default."
        ),
    )

    parser.add_argument(
        "--llm-model",
        help=(
            "Optional model override when using "
            "--planner llm."
        ),
    )

    parser.add_argument(
        "--skip-frontend-build",
        action="store_true",
        help=(
            "Skip the npm production-build test. "
            "Useful when node_modules is unavailable."
        ),
    )

    parser.add_argument(
        "--max-repair-attempts",
        type=int,
        default=1,
        help=(
            "Maximum automatic repair attempts. "
            "Allowed range: 0 to 3. Default: 1."
        ),
    )

    parser.add_argument(
        "--skip-security-scan",
        action="store_true",
        help="Skip generated-code security scanning.",
    )

    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Skip generated-project evaluation.",
    )

    parser.add_argument(
        "--minimum-score",
        type=float,
        default=80.0,
        help=(
            "Minimum acceptable quality score. "
            "Default: 80."
        ),
    )

    args = parser.parse_args()

    requirement = args.requirement

    if not requirement:
        requirement = input(
            "Describe the application you want to build: "
        )

    if args.generate:
        try:
            result = run_workflow(
                requirement,
                overwrite=args.force,
                planner=args.planner,
                llm_model=args.llm_model,
                run_frontend_build=(
                    not args.skip_frontend_build
                ),
                max_repair_attempts=(
                    args.max_repair_attempts
                ),
                skip_security_scan=(
                    args.skip_security_scan
                ),
                skip_evaluation=(
                    args.skip_evaluation
                ),
                minimum_score=args.minimum_score,
            )
        except (
            ValueError,
            FileExistsError,
            RuntimeError,
        ) as error:
            parser.error(str(error))
        except PermissionError:
            parser.error(
                "The generated project is being used by "
                "another process. Stop Node, Vite, FastAPI, "
                "and close files opened inside its folder."
            )

        plan = result["plan"]

        print("\nProject plan")
        print("------------")
        print(
            json.dumps(
                plan.to_dict(),
                indent=2,
            )
        )

        print(
            "\nProject generated at: "
            f"{result['project_directory']}"
        )

        print(
            "Planner used: "
            f"{result.get('planner_used', 'heuristic')}"
        )

        print_test_summary(
            result.get("test_report")
        )

        print_repair_summary(
            result.get(
                "repair_attempts",
                0,
            ),
            result.get(
                "repair_history",
                [],
            ),
        )

        print_security_summary(
            result.get("security_report")
        )

        print_evaluation_summary(
            result.get("evaluation_report")
        )

        print("\nLangGraph workflow")
        print("------------------")
        print(
            f"Final status: {result['status']}"
        )

        if result["status"] != "passed":
            raise SystemExit(2)

        return

    try:
        plan = create_plan_only(
            requirement,
            planner=args.planner,
            llm_model=args.llm_model,
        )
    except (
        ValueError,
        RuntimeError,
    ) as error:
        parser.error(str(error))

    plan_data = plan.to_dict()

    print(
        json.dumps(
            plan_data,
            indent=2,
        )
    )

    print(
        f"\nPlanner used: {args.planner}"
    )

    if args.save:
        output_file = save_plan(
            plan.project_name,
            plan_data,
        )

        print(
            f"\nPlan saved to: {output_file}"
        )


if __name__ == "__main__":
    main()