import tempfile
import unittest
from pathlib import Path

from src.agents.generator import generate_project
from src.agents.planner import plan_project


class GeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = plan_project(
            "Build a React booking platform using FastAPI "
            "and PostgreSQL with login and payments."
        )

    def test_generates_connected_full_stack_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            project_directory = generate_project(
                self.plan,
                output_root=Path(temp_directory),
            )

            expected_files = [
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

            for relative_path in expected_files:
                self.assertTrue(
                    (project_directory / relative_path).exists(),
                    f"Missing generated file: {relative_path}",
                )

            backend_code = (
                project_directory / "backend/app/main.py"
            ).read_text(encoding="utf-8")

            frontend_code = (
                project_directory / "frontend/src/App.jsx"
            ).read_text(encoding="utf-8")

            self.assertIn("CORSMiddleware", backend_code)
            self.assertIn('@app.get("/api/project")', backend_code)
            self.assertIn('"status": "connected"', backend_code)

            self.assertIn("useEffect", frontend_code)
            self.assertIn("fetch(", frontend_code)
            self.assertIn("/api/project", frontend_code)

    def test_prevents_accidental_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            generate_project(
                self.plan,
                output_root=Path(temp_directory),
            )

            with self.assertRaises(FileExistsError):
                generate_project(
                    self.plan,
                    output_root=Path(temp_directory),
                )

    def test_allows_explicit_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            project_directory = generate_project(
                self.plan,
                output_root=Path(temp_directory),
            )

            temporary_file = project_directory / "temporary.txt"
            temporary_file.write_text(
                "This file should be removed.",
                encoding="utf-8",
            )

            regenerated_directory = generate_project(
                self.plan,
                output_root=Path(temp_directory),
                overwrite=True,
            )

            self.assertEqual(
                project_directory,
                regenerated_directory,
            )
            self.assertFalse(temporary_file.exists())


if __name__ == "__main__":
    unittest.main()