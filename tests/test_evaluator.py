import tempfile
import unittest
from pathlib import Path

from src.agents.generator import generate_project
from src.agents.planner import plan_project
from src.evaluation.evaluator import (
    evaluate_project,
    write_evaluation_report,
)
from src.security.scanner import write_report


class EvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = plan_project(
            "Build a React booking platform using FastAPI "
            "and PostgreSQL with login and payments."
        )

    def test_generated_project_passes_evaluation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            project_directory = generate_project(
                self.plan,
                output_root=Path(temp_directory),
            )

            write_report(project_directory)

            result = evaluate_project(
                project_directory
            )

            self.assertEqual(
                result["status"],
                "passed",
            )

            self.assertEqual(
                result["overall_score"],
                100.0,
            )

    def test_missing_file_reduces_score(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            project_directory = generate_project(
                self.plan,
                output_root=Path(temp_directory),
            )

            write_report(project_directory)

            package_file = (
                project_directory
                / "frontend"
                / "package.json"
            )

            package_file.unlink()

            result = evaluate_project(
                project_directory
            )

            self.assertNotEqual(
                result["status"],
                "passed",
            )

            self.assertLess(
                result["overall_score"],
                100.0,
            )

    def test_writes_evaluation_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            project_directory = generate_project(
                self.plan,
                output_root=Path(temp_directory),
            )

            write_report(project_directory)

            report_path = write_evaluation_report(
                project_directory
            )

            self.assertTrue(report_path.exists())


if __name__ == "__main__":
    unittest.main()