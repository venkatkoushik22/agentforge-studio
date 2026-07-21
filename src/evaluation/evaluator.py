import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    "README.md",
    "project_plan.json",
    "manifest.json",
    "backend/app/main.py",
    "backend/requirements.txt",
    "frontend/package.json",
    "frontend/index.html",
    "frontend/src/main.jsx",
    "frontend/src/App.jsx",
]


@dataclass(slots=True)
class EvaluationCheck:
    name: str
    passed: bool
    details: str


def _check_required_files(
    project_directory: Path,
) -> EvaluationCheck:
    missing_files = [
        relative_path
        for relative_path in REQUIRED_FILES
        if not (project_directory / relative_path).exists()
    ]

    if missing_files:
        return EvaluationCheck(
            name="required_files",
            passed=False,
            details=(
                "Missing required files: "
                + ", ".join(missing_files)
            ),
        )

    return EvaluationCheck(
        name="required_files",
        passed=True,
        details="All required project files exist.",
    )


def _check_backend_syntax(
    project_directory: Path,
) -> EvaluationCheck:
    backend_file = (
        project_directory
        / "backend"
        / "app"
        / "main.py"
    )

    if not backend_file.exists():
        return EvaluationCheck(
            name="backend_syntax",
            passed=False,
            details="Backend entry point does not exist.",
        )

    try:
        backend_source = backend_file.read_text(
            encoding="utf-8"
        )

        compile(
            backend_source,
            str(backend_file),
            "exec",
        )
    except (OSError, SyntaxError) as error:
        return EvaluationCheck(
            name="backend_syntax",
            passed=False,
            details=f"Backend syntax error: {error}",
        )

    return EvaluationCheck(
        name="backend_syntax",
        passed=True,
        details="Backend Python syntax is valid.",
    )


def _check_frontend_package(
    project_directory: Path,
) -> EvaluationCheck:
    package_file = (
        project_directory
        / "frontend"
        / "package.json"
    )

    if not package_file.exists():
        return EvaluationCheck(
            name="frontend_package",
            passed=False,
            details="frontend/package.json does not exist.",
        )

    try:
        package_data = json.loads(
            package_file.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as error:
        return EvaluationCheck(
            name="frontend_package",
            passed=False,
            details=f"Invalid package.json: {error}",
        )

    scripts = package_data.get("scripts", {})
    dependencies = package_data.get("dependencies", {})

    missing_items = []

    if "dev" not in scripts:
        missing_items.append("dev script")

    if "build" not in scripts:
        missing_items.append("build script")

    if "react" not in dependencies:
        missing_items.append("React dependency")

    if "react-dom" not in dependencies:
        missing_items.append("React DOM dependency")

    if missing_items:
        return EvaluationCheck(
            name="frontend_package",
            passed=False,
            details=(
                "Missing frontend configuration: "
                + ", ".join(missing_items)
            ),
        )

    return EvaluationCheck(
        name="frontend_package",
        passed=True,
        details="Frontend package configuration is valid.",
    )


def _check_api_contract(
    project_directory: Path,
) -> EvaluationCheck:
    backend_file = (
        project_directory
        / "backend"
        / "app"
        / "main.py"
    )

    frontend_file = (
        project_directory
        / "frontend"
        / "src"
        / "App.jsx"
    )

    if not backend_file.exists() or not frontend_file.exists():
        return EvaluationCheck(
            name="api_contract",
            passed=False,
            details=(
                "Backend or frontend source file is missing."
            ),
        )

    backend_code = backend_file.read_text(
        encoding="utf-8"
    )

    frontend_code = frontend_file.read_text(
        encoding="utf-8"
    )

    backend_has_endpoint = (
        '@app.get("/api/project")' in backend_code
    )

    frontend_calls_endpoint = (
        "/api/project" in frontend_code
        and "fetch(" in frontend_code
    )

    if not backend_has_endpoint:
        return EvaluationCheck(
            name="api_contract",
            passed=False,
            details=(
                "Backend does not define /api/project."
            ),
        )

    if not frontend_calls_endpoint:
        return EvaluationCheck(
            name="api_contract",
            passed=False,
            details=(
                "Frontend does not call /api/project."
            ),
        )

    return EvaluationCheck(
        name="api_contract",
        passed=True,
        details=(
            "Frontend and backend share the expected API contract."
        ),
    )


def _check_security_report(
    project_directory: Path,
) -> EvaluationCheck:
    report_file = (
        project_directory / "security_report.json"
    )

    if not report_file.exists():
        return EvaluationCheck(
            name="security_scan",
            passed=False,
            details="Security report has not been generated.",
        )

    try:
        report = json.loads(
            report_file.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as error:
        return EvaluationCheck(
            name="security_scan",
            passed=False,
            details=f"Invalid security report: {error}",
        )

    total_findings = report.get("total_findings", 0)
    status = report.get("status")

    if status != "passed" or total_findings > 0:
        return EvaluationCheck(
            name="security_scan",
            passed=False,
            details=(
                f"Security scan reported "
                f"{total_findings} finding(s)."
            ),
        )

    return EvaluationCheck(
        name="security_scan",
        passed=True,
        details="Security scan passed with zero findings.",
    )


def evaluate_project(
    project_directory: Path | str,
) -> dict[str, Any]:
    project_directory = Path(project_directory).resolve()

    if not project_directory.exists():
        raise FileNotFoundError(
            f"Project does not exist: {project_directory}"
        )

    if not project_directory.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: {project_directory}"
        )

    checks = [
        _check_required_files(project_directory),
        _check_backend_syntax(project_directory),
        _check_frontend_package(project_directory),
        _check_api_contract(project_directory),
        _check_security_report(project_directory),
    ]

    passed_checks = sum(
        check.passed for check in checks
    )

    total_checks = len(checks)

    overall_score = round(
        (passed_checks / total_checks) * 100,
        1,
    )

    if overall_score == 100:
        status = "passed"
    elif overall_score >= 80:
        status = "warning"
    else:
        status = "failed"

    return {
        "project": str(project_directory),
        "status": status,
        "overall_score": overall_score,
        "passed_checks": passed_checks,
        "total_checks": total_checks,
        "checks": [
            asdict(check)
            for check in checks
        ],
    }


def write_evaluation_report(
    project_directory: Path | str,
    output_file: Path | str | None = None,
) -> Path:
    project_directory = Path(project_directory)
    report = evaluate_project(project_directory)

    report_path = (
        Path(output_file)
        if output_file
        else project_directory / "evaluation_report.json"
    )

    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the quality and completeness "
            "of a generated AgentForge project."
        )
    )

    parser.add_argument(
        "project_directory",
        help="Path to the generated project.",
    )

    parser.add_argument(
        "--output",
        help="Optional evaluation report path.",
    )

    args = parser.parse_args()

    try:
        report = evaluate_project(
            args.project_directory
        )
    except (
        FileNotFoundError,
        NotADirectoryError,
    ) as error:
        parser.error(str(error))

    print(json.dumps(report, indent=2))

    report_path = write_evaluation_report(
        args.project_directory,
        args.output,
    )

    print(
        f"\nEvaluation report saved to: {report_path}"
    )


if __name__ == "__main__":
    main()