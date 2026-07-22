import tempfile
import unittest
from pathlib import Path

from src.agents.generator import (
    generate_project,
)
from src.agents.planner import (
    plan_project,
)
from src.agents.repairer import (
    repair_project,
)
from src.agents.tester import (
    test_generated_project,
)


class RepairAgentTests(
    unittest.TestCase
):
    def test_repairs_broken_backend(
        self,
    ) -> None:
        plan = plan_project(
            "Build a React booking platform "
            "using FastAPI and PostgreSQL "
            "with login."
        )

        with tempfile.TemporaryDirectory() as directory:
            project_directory = generate_project(
                plan,
                output_root=Path(
                    directory
                ),
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

            failed_report = (
                test_generated_project(
                    project_directory,
                    run_frontend_build=False,
                )
            )

            self.assertEqual(
                failed_report["status"],
                "failed",
            )

            repair_result = repair_project(
                plan,
                project_directory,
                failed_report,
                attempt=1,
            )

            self.assertEqual(
                repair_result["status"],
                "completed",
            )

            repaired_report = (
                test_generated_project(
                    project_directory,
                    run_frontend_build=False,
                )
            )

            self.assertEqual(
                repaired_report["status"],
                "passed",
            )


if __name__ == "__main__":
    unittest.main()