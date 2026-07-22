import tempfile
import unittest
from pathlib import Path

from src.agents.generator import generate_project
from src.agents.planner import plan_project
from src.agents.tester import (
    test_generated_project,
    write_test_report,
)


class GeneratedProjectTesterTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.plan = plan_project(
            "Build a React booking platform using "
            "FastAPI and PostgreSQL with login."
        )

    def test_valid_project_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_directory = generate_project(
                self.plan,
                output_root=Path(directory),
            )

            result = test_generated_project(
                project_directory,
                run_frontend_build=False,
            )

            self.assertEqual(
                result["status"],
                "passed",
            )

            self.assertEqual(
                result["failed_checks"],
                0,
            )

    def test_invalid_backend_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_directory = generate_project(
                self.plan,
                output_root=Path(directory),
            )

            backend_file = (
                project_directory
                / "backend"
                / "app"
                / "main.py"
            )

            backend_file.write_text(
                "def broken(:\n",
                encoding="utf-8",
            )

            result = test_generated_project(
                project_directory,
                run_frontend_build=False,
            )

            self.assertEqual(
                result["status"],
                "failed",
            )

            failed_names = {
                check["name"]
                for check in result["checks"]
                if check["status"] == "failed"
            }

            self.assertIn(
                "backend_compile",
                failed_names,
            )

    def test_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_directory = generate_project(
                self.plan,
                output_root=Path(directory),
            )

            report_path = write_test_report(
                project_directory,
                run_frontend_build=False,
            )

            self.assertTrue(
                report_path.exists()
            )


if __name__ == "__main__":
    unittest.main()