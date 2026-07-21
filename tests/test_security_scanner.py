import json
import tempfile
import unittest
from pathlib import Path

from src.security.scanner import scan_project, write_report


class SecurityScannerTests(unittest.TestCase):
    def test_detects_security_issues(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            project_directory = Path(temp_directory)

            unsafe_file = project_directory / "unsafe.py"
            unsafe_file.write_text(
                'api_key = "example-secret-value"\n'
                'result = eval(user_input)\n',
                encoding="utf-8",
            )

            findings = scan_project(project_directory)
            detected_rules = {
                finding.rule_id
                for finding in findings
            }

            self.assertIn(
                "hardcoded-secret",
                detected_rules,
            )
            self.assertIn(
                "python-eval",
                detected_rules,
            )

    def test_creates_security_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            project_directory = Path(temp_directory)

            safe_file = project_directory / "safe.py"
            safe_file.write_text(
                'message = "hello"\n',
                encoding="utf-8",
            )

            report_path = write_report(project_directory)

            self.assertTrue(report_path.exists())

            report = json.loads(
                report_path.read_text(encoding="utf-8")
            )

            self.assertEqual(
                report["status"],
                "passed",
            )
            self.assertEqual(
                report["total_findings"],
                0,
            )


if __name__ == "__main__":
    unittest.main()