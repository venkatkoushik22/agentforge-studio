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
    """Save a project plan without generating an application."""
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


def print_security_summary(
    report: dict[str, Any] | None,
) -> None:
    """Display the security-scan result."""
    print("\nSecurity scan")
    print("-------------")

    if report is None:
        print("Status: skipped")
        return

    severity_counts = report["severity_counts"]

    print(f"Status: {report['status']}")
    print(
        f"Total findings: "
        f"{report['total_findings']}"
    )
    print(
        f"Critical: "
        f"{severity_counts['CRITICAL']}"
    )
    print(f"High: {severity_counts['HIGH']}")
    print(f"Medium: {severity_counts['MEDIUM']}")
    print(f"Low: {severity_counts['LOW']}")


def print_evaluation_summary(
    report: dict[str, Any] | None,
) -> None:
    """Display the project-quality evaluation."""
    print("\nQuality evaluation")
    print("------------------")

    if report is None:
        print("Status: skipped")
        return

    print(f"Status: {report['status']}")
    print(f"Score: {report['overall_score']}%")
    print(
        f"Checks passed: "
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
            "Plan and generate full-stack applications "
            "through the AgentForge LangGraph workflow."
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
        help=(
            "Run the complete LangGraph generation "
            "workflow."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing generated project.",
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
        ) as error:
            parser.error(str(error))
        except PermissionError:
            parser.error(
                "The generated folder is being used by "
                "another process. Stop Node, Vite, "
                "FastAPI, and close files opened inside "
                "the generated project."
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
            f"\nProject generated at: "
            f"{result['project_directory']}"
        )

        print_security_summary(
            result.get("security_report")
        )

        print_evaluation_summary(
            result.get("evaluation_report")
        )

        print("\nLangGraph workflow")
        print("------------------")
        print(f"Final status: {result['status']}")

        if result["status"] != "passed":
            raise SystemExit(2)

        return

    try:
        plan = plan_project(requirement)
    except ValueError as error:
        parser.error(str(error))

    plan_data = plan.to_dict()

    print(
        json.dumps(
            plan_data,
            indent=2,
        )
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