import argparse
import json
from pathlib import Path

from src.agents.planner import plan_project


def save_plan(project_name: str, plan_data: dict) -> Path:
    """Save the project plan inside the generated-project directory."""
    project_directory = Path("generated_projects") / project_name
    project_directory.mkdir(parents=True, exist_ok=True)

    output_file = project_directory / "project_plan.json"
    output_file.write_text(
        json.dumps(plan_data, indent=2),
        encoding="utf-8",
    )

    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a structured application plan from a requirement."
    )

    parser.add_argument(
        "requirement",
        nargs="?",
        help="Natural-language description of the application.",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the generated plan as a JSON file.",
    )

    args = parser.parse_args()

    requirement = args.requirement

    if not requirement:
        requirement = input("Describe the application you want to build: ")

    try:
        plan = plan_project(requirement)
    except ValueError as error:
        parser.error(str(error))

    plan_data = plan.to_dict()
    print(json.dumps(plan_data, indent=2))

    if args.save:
        output_file = save_plan(plan.project_name, plan_data)
        print(f"\nPlan saved to: {output_file}")


if __name__ == "__main__":
    main()