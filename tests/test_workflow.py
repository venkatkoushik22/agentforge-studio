import tempfile
import unittest
from pathlib import Path

from src.core.workflow import run_workflow


class WorkflowTests(unittest.TestCase):
    def test_complete_workflow_passes(self) -> None:
        requirement = (
            "Build a React booking platform using FastAPI "
            "and PostgreSQL with login and payments."
        )

        with tempfile.TemporaryDirectory() as temp_directory:
            result = run_workflow(
                requirement,
                output_root=Path(temp_directory),
                minimum_score=90,
            )

            self.assertEqual(
                result["status"],
                "passed",
            )

            self.assertTrue(
                result["project_directory"].exists()
            )

            self.assertEqual(
                result["security_report"]["status"],
                "passed",
            )

            self.assertEqual(
                result["evaluation_report"][
                    "overall_score"
                ],
                100.0,
            )

    def test_quality_gate_can_fail(self) -> None:
        requirement = (
            "Build a React inventory application "
            "using FastAPI."
        )

        with tempfile.TemporaryDirectory() as temp_directory:
            result = run_workflow(
                requirement,
                output_root=Path(temp_directory),
                skip_security_scan=True,
                minimum_score=90,
            )

            self.assertEqual(
                result["status"],
                "failed",
            )

            self.assertLess(
                result["evaluation_report"][
                    "overall_score"
                ],
                90,
            )

    def test_rejects_empty_requirement(self) -> None:
        with self.assertRaises(ValueError):
            run_workflow("   ")


if __name__ == "__main__":
    unittest.main()