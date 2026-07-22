import argparse
import json
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal


TestStatus = Literal[
    "passed",
    "failed",
    "skipped",
]


@dataclass(slots=True)
class TestCheck:
    """Result from one generated-project test."""

    name: str
    status: TestStatus
    details: str
    duration_ms: float


def _timed_check(
    name: str,
    check_function,
) -> TestCheck:
    """Execute a test function and record its duration."""
    start_time = time.perf_counter()

    try:
        status, details = check_function()
    except Exception as error:
        status = "failed"
        details = (
            f"Unexpected test error: "
            f"{type(error).__name__}: {error}"
        )

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    return TestCheck(
        name=name,
        status=status,
        details=details,
        duration_ms=duration_ms,
    )


def _check_manifest(
    project_directory: Path,
) -> tuple[TestStatus, str]:
    """Confirm every file listed in the manifest exists."""
    manifest_file = (
        project_directory / "manifest.json"
    )

    if not manifest_file.exists():
        return (
            "failed",
            "manifest.json does not exist.",
        )

    try:
        manifest = json.loads(
            manifest_file.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as error:
        return (
            "failed",
            f"manifest.json is invalid: {error}",
        )

    expected_files = manifest.get(
        "generated_files",
        [],
    )

    if not expected_files:
        return (
            "failed",
            "Manifest does not list generated files.",
        )

    missing_files = [
        relative_path
        for relative_path in expected_files
        if not (
            project_directory / relative_path
        ).exists()
    ]

    if missing_files:
        return (
            "failed",
            "Missing generated files: "
            + ", ".join(missing_files),
        )

    return (
        "passed",
        (
            f"All {len(expected_files)} manifest "
            "files exist."
        ),
    )


def _check_backend_compile(
    project_directory: Path,
) -> tuple[TestStatus, str]:
    """Compile the generated backend with Python."""
    backend_file = (
        project_directory
        / "backend"
        / "app"
        / "main.py"
    )

    if not backend_file.exists():
        return (
            "failed",
            "backend/app/main.py does not exist.",
        )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "py_compile",
            str(backend_file),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    if result.returncode != 0:
        error_message = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Unknown compilation failure."
        )

        return (
            "failed",
            f"Backend compilation failed: {error_message}",
        )

    return (
        "passed",
        "Generated backend Python syntax is valid.",
    )


def _check_backend_contract(
    project_directory: Path,
) -> tuple[TestStatus, str]:
    """Confirm expected API endpoints and CORS exist."""
    backend_file = (
        project_directory
        / "backend"
        / "app"
        / "main.py"
    )

    if not backend_file.exists():
        return (
            "failed",
            "Backend source file does not exist.",
        )

    backend_code = backend_file.read_text(
        encoding="utf-8"
    )

    required_fragments = {
        "health endpoint": '@app.get("/health")',
        "project endpoint": '@app.get("/api/project")',
        "CORS middleware": "CORSMiddleware",
        "connected status": '"status": "connected"',
    }

    missing_items = [
        description
        for description, fragment
        in required_fragments.items()
        if fragment not in backend_code
    ]

    if missing_items:
        return (
            "failed",
            "Backend is missing: "
            + ", ".join(missing_items),
        )

    return (
        "passed",
        "Backend API contract is present.",
    )


def _check_frontend_configuration(
    project_directory: Path,
) -> tuple[TestStatus, str]:
    """Validate package.json and React entry files."""
    frontend_directory = (
        project_directory / "frontend"
    )

    package_file = (
        frontend_directory / "package.json"
    )

    app_file = (
        frontend_directory
        / "src"
        / "App.jsx"
    )

    main_file = (
        frontend_directory
        / "src"
        / "main.jsx"
    )

    if not package_file.exists():
        return (
            "failed",
            "frontend/package.json does not exist.",
        )

    try:
        package_data = json.loads(
            package_file.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as error:
        return (
            "failed",
            f"package.json is invalid: {error}",
        )

    scripts = package_data.get(
        "scripts",
        {},
    )

    dependencies = package_data.get(
        "dependencies",
        {},
    )

    missing_configuration = []

    if "dev" not in scripts:
        missing_configuration.append(
            "dev script"
        )

    if "build" not in scripts:
        missing_configuration.append(
            "build script"
        )

    if "react" not in dependencies:
        missing_configuration.append(
            "React dependency"
        )

    if "react-dom" not in dependencies:
        missing_configuration.append(
            "React DOM dependency"
        )

    if not app_file.exists():
        missing_configuration.append(
            "src/App.jsx"
        )

    if not main_file.exists():
        missing_configuration.append(
            "src/main.jsx"
        )

    if missing_configuration:
        return (
            "failed",
            "Frontend is missing: "
            + ", ".join(missing_configuration),
        )

    app_code = app_file.read_text(
        encoding="utf-8"
    )

    if (
        "/api/project" not in app_code
        or "fetch(" not in app_code
    ):
        return (
            "failed",
            (
                "Frontend does not call the generated "
                "/api/project endpoint."
            ),
        )

    return (
        "passed",
        "Frontend configuration and API call are valid.",
    )


def _find_npm() -> str | None:
    """Locate npm on Windows, macOS, or Linux."""
    return (
        shutil.which("npm")
        or shutil.which("npm.cmd")
    )


def _check_frontend_build(
    project_directory: Path,
) -> tuple[TestStatus, str]:
    """Run the Vite production build when dependencies exist."""
    frontend_directory = (
        project_directory / "frontend"
    )

    node_modules = (
        frontend_directory / "node_modules"
    )

    if not node_modules.exists():
        return (
            "skipped",
            (
                "Frontend build skipped because "
                "node_modules is not installed."
            ),
        )

    npm_command = _find_npm()

    if npm_command is None:
        return (
            "skipped",
            "Frontend build skipped because npm was not found.",
        )

    result = subprocess.run(
        [
            npm_command,
            "run",
            "build",
        ],
        cwd=frontend_directory,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        shell=False,
    )

    if result.returncode != 0:
        error_message = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Unknown frontend build failure."
        )

        return (
            "failed",
            f"Frontend build failed: {error_message}",
        )

    return (
        "passed",
        "Vite production build completed successfully.",
    )


def test_generated_project(
    project_directory: Path | str,
    *,
    run_frontend_build: bool = True,
) -> dict:
    """Run automated validation against a generated project."""
    project_directory = Path(
        project_directory
    ).resolve()

    if not project_directory.exists():
        raise FileNotFoundError(
            f"Project does not exist: "
            f"{project_directory}"
        )

    if not project_directory.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: "
            f"{project_directory}"
        )

    checks = [
        _timed_check(
            "manifest",
            lambda: _check_manifest(
                project_directory
            ),
        ),
        _timed_check(
            "backend_compile",
            lambda: _check_backend_compile(
                project_directory
            ),
        ),
        _timed_check(
            "backend_contract",
            lambda: _check_backend_contract(
                project_directory
            ),
        ),
        _timed_check(
            "frontend_configuration",
            lambda: _check_frontend_configuration(
                project_directory
            ),
        ),
    ]

    if run_frontend_build:
        checks.append(
            _timed_check(
                "frontend_build",
                lambda: _check_frontend_build(
                    project_directory
                ),
            )
        )

    passed_checks = sum(
        check.status == "passed"
        for check in checks
    )

    failed_checks = sum(
        check.status == "failed"
        for check in checks
    )

    skipped_checks = sum(
        check.status == "skipped"
        for check in checks
    )

    status = (
        "failed"
        if failed_checks
        else "passed"
    )

    return {
        "project": str(project_directory),
        "status": status,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "skipped_checks": skipped_checks,
        "total_checks": len(checks),
        "checks": [
            asdict(check)
            for check in checks
        ],
    }


def write_test_report(
    project_directory: Path | str,
    output_file: Path | str | None = None,
    *,
    run_frontend_build: bool = True,
) -> Path:
    """Run tests and save the JSON report."""
    project_directory = Path(
        project_directory
    )

    report = test_generated_project(
        project_directory,
        run_frontend_build=run_frontend_build,
    )

    report_path = (
        Path(output_file)
        if output_file
        else project_directory / "test_report.json"
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run automated tests against an "
            "AgentForge-generated application."
        )
    )

    parser.add_argument(
        "project_directory",
        help="Path to the generated project.",
    )

    parser.add_argument(
        "--skip-frontend-build",
        action="store_true",
        help=(
            "Skip the optional npm production "
            "build test."
        ),
    )

    parser.add_argument(
        "--output",
        help="Optional JSON report output path.",
    )

    args = parser.parse_args()

    try:
        report_path = write_test_report(
            args.project_directory,
            args.output,
            run_frontend_build=(
                not args.skip_frontend_build
            ),
        )
    except (
        FileNotFoundError,
        NotADirectoryError,
    ) as error:
        parser.error(str(error))

    report = json.loads(
        report_path.read_text(
            encoding="utf-8"
        )
    )

    print(
        json.dumps(
            report,
            indent=2,
        )
    )

    print(
        f"\nTest report saved to: "
        f"{report_path}"
    )

    if report["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()