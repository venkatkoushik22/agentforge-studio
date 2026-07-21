import argparse
import json
from pathlib import Path
from typing import Any

from src.agents.generator import generate_project
from src.agents.planner import plan_project
from src.evaluation.evaluator import write_evaluation_report
from src.security.scanner import write_report


def save_plan(
    project_name: str,
    plan_data: dict[str, Any],
) -> Path:
    """Save only the generated JSON project plan."""
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


def load_json_report(report_path: Path) -> dict[str, Any]:
    """Load a JSON report from disk."""
    return json.loads(
        report_path.read_text(encoding="utf-8")
    )


def run_security_scan(
    project_directory: Path,
) -> dict[str, Any]:
    """Run the security scanner and display a summary."""
    report_path = write_report(project_directory)
    report = load_json_report(report_path)

    severity_counts = report["severity_counts"]

    print("\nSecurity scan")
    print("-------------")
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
    print(f"Report: {report_path}")

    return report


def run_evaluation(
    project_directory: Path,
) -> dict[str, Any]:
    """Evaluate the generated project and display a summary."""
    report_path = write_evaluation_report(
        project_directory
    )

    report = load_json_report(report_path)

    print("\nQuality evaluation")
    print("------------------")
    print(f"Status: {report['status']}")
    print(
        f"Score: {report['overall_score']}%"
    )
    print(
        f"Checks passed: "
        f"{report['passed_checks']}/"
        f"{report['total_checks']}"
    )

    for check in report["checks"]:
        marker = "PASS" if check["passed"] else "FAIL"

        print(
            f"[{marker}] {check['name']}: "
            f"{check['details']}"
        )

    print(f"Report: {report_path}")

    return report


def validate_minimum_score(
    minimum_score: float,
) -> None:
    """Validate the requested quality threshold."""
    if minimum_score < 0 or minimum_score > 100:
        raise ValueError(
            "Minimum score must be between 0 and 100."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Plan, generate, scan, and evaluate "
            "full-stack application scaffolds."
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
        help="Save only the JSON project plan.",
    )

    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate a FastAPI and React project.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing generated project.",
    )

    parser.add_argument(
        "--skip-security-scan",
        action="store_true",
        help="Skip the generated-code security scan.",
    )

    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Skip the generated-project quality evaluation.",
    )

    parser.add_argument(
        "--minimum-score",
        type=float,
        default=80.0,
        help=(
            "Minimum acceptable evaluation score. "
            "Default: 80."
        ),
    )

    args = parser.parse_args()

    try:
        validate_minimum_score(
            args.minimum_score
        )
    except ValueError as error:
        parser.error(str(error))

    requirement = args.requirement

    if not requirement:
        requirement = input(
            "Describe the application you want to build: "
        )

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

    if args.generate:
        try:
            project_directory = generate_project(
                plan,
                overwrite=args.force,
            )
        except FileExistsError as error:
            parser.error(str(error))
        except PermissionError:
            parser.error(
                "The generated project is being used by "
                "another process. Stop Vite, Node, FastAPI, "
                "and close editors opened inside the folder."
            )

        print(
            f"\nProject generated at: "
            f"{project_directory}"
        )

        if not args.skip_security_scan:
            run_security_scan(project_directory)

        if not args.skip_evaluation:
            evaluation = run_evaluation(
                project_directory
            )

            score = evaluation["overall_score"]

            if score < args.minimum_score:
                print(
                    "\nQuality gate failed: "
                    f"{score}% is below the required "
                    f"{args.minimum_score}%."
                )

                raise SystemExit(2)

            print(
                "\nQuality gate passed: "
                f"{score}% meets the required "
                f"{args.minimum_score}%."
            )

    elif args.save:
        output_file = save_plan(
            plan.project_name,
            plan_data,
        )

        print(
            f"\nPlan saved to: {output_file}"
        )


if __name__ == "__main__":
    main()