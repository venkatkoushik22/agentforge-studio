import argparse
import json
from pathlib import Path

from src.agents.generator import generate_project
from src.agents.planner import plan_project


def save_plan(project_name: str, plan_data: dict) -> Path:
    """Save only the generated JSON plan."""
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
        description="Plan and generate application scaffolds."
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

    args = parser.parse_args()

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
    print(json.dumps(plan_data, indent=2))

    if args.generate:
        try:
            project_directory = generate_project(
                plan,
                overwrite=args.force,
            )
        except FileExistsError as error:
            parser.error(str(error))

        print(f"\nProject generated at: {project_directory}")

    elif args.save:
        output_file = save_plan(
            plan.project_name,
            plan_data,
        )

        print(f"\nPlan saved to: {output_file}")


if __name__ == "__main__":
    main()