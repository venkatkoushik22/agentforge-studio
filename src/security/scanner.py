import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


SCANNABLE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".env",
}

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
}

SECURITY_PATTERNS = [
    {
        "rule_id": "hardcoded-secret",
        "severity": "HIGH",
        "description": "Possible hard-coded password, token, secret, or API key.",
        "pattern": re.compile(
            r"""(?ix)
            \b(api[_-]?key|password|secret|access[_-]?token|auth[_-]?token)\b
            \s*[:=]\s*
            ["'][^"']{6,}["']
            """
        ),
    },
    {
        "rule_id": "aws-access-key",
        "severity": "CRITICAL",
        "description": "Possible AWS access key detected.",
        "pattern": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    },
    {
        "rule_id": "private-key",
        "severity": "CRITICAL",
        "description": "Private key material may be present.",
        "pattern": re.compile(
            r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"
        ),
    },
    {
        "rule_id": "python-eval",
        "severity": "HIGH",
        "description": "Dynamic code execution through eval or exec.",
        "pattern": re.compile(r"\b(eval|exec)\s*\("),
    },
    {
        "rule_id": "os-system",
        "severity": "HIGH",
        "description": "Operating-system command execution detected.",
        "pattern": re.compile(r"\bos\.system\s*\("),
    },
    {
        "rule_id": "subprocess-shell",
        "severity": "HIGH",
        "description": "Subprocess execution with shell=True detected.",
        "pattern": re.compile(
            r"\bsubprocess\.[a-zA-Z_]+\s*\([^)]*shell\s*=\s*True"
        ),
    },
    {
        "rule_id": "javascript-eval",
        "severity": "HIGH",
        "description": "JavaScript dynamic evaluation detected.",
        "pattern": re.compile(r"\beval\s*\("),
    },
    {
        "rule_id": "node-command-execution",
        "severity": "HIGH",
        "description": "Node.js command execution detected.",
        "pattern": re.compile(
            r"\b(child_process\.)?(exec|execSync)\s*\("
        ),
    },
    {
        "rule_id": "cors-wildcard",
        "severity": "MEDIUM",
        "description": "Wildcard CORS configuration detected.",
        "pattern": re.compile(
            r"""allow_origins\s*=\s*\[\s*["']\*["']\s*\]"""
        ),
    },
]


@dataclass(slots=True)
class SecurityFinding:
    rule_id: str
    severity: str
    description: str
    file: str
    line: int
    evidence: str


def _should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRECTORIES for part in path.parts)


def _is_scannable(path: Path) -> bool:
    if path.name.startswith(".env"):
        return True

    return path.suffix.lower() in SCANNABLE_EXTENSIONS


def scan_file(
    file_path: Path,
    project_root: Path,
) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []

    try:
        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except OSError:
        return findings

    for line_number, line in enumerate(
        content.splitlines(),
        start=1,
    ):
        for rule in SECURITY_PATTERNS:
            if rule["pattern"].search(line):
                findings.append(
                    SecurityFinding(
                        rule_id=rule["rule_id"],
                        severity=rule["severity"],
                        description=rule["description"],
                        file=str(
                            file_path.relative_to(project_root)
                        ),
                        line=line_number,
                        evidence=line.strip()[:160],
                    )
                )

    return findings


def scan_project(
    project_directory: Path | str,
) -> list[SecurityFinding]:
    project_root = Path(project_directory).resolve()

    if not project_root.exists():
        raise FileNotFoundError(
            f"Project directory does not exist: {project_root}"
        )

    if not project_root.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: {project_root}"
        )

    findings: list[SecurityFinding] = []

    for file_path in project_root.rglob("*"):
        if not file_path.is_file():
            continue

        if _should_ignore(file_path):
            continue

        if not _is_scannable(file_path):
            continue

        findings.extend(
            scan_file(
                file_path=file_path,
                project_root=project_root,
            )
        )

    return findings


def build_report(
    project_directory: Path | str,
    findings: list[SecurityFinding],
) -> dict:
    severity_counts = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }

    for finding in findings:
        severity_counts[finding.severity] += 1

    return {
        "project": str(Path(project_directory).resolve()),
        "status": "failed" if findings else "passed",
        "total_findings": len(findings),
        "severity_counts": severity_counts,
        "findings": [
            asdict(finding)
            for finding in findings
        ],
    }


def write_report(
    project_directory: Path | str,
    output_file: Path | str | None = None,
) -> Path:
    project_directory = Path(project_directory)
    findings = scan_project(project_directory)
    report = build_report(project_directory, findings)

    report_path = (
        Path(output_file)
        if output_file
        else project_directory / "security_report.json"
    )

    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan a generated project for common security risks."
    )

    parser.add_argument(
        "project_directory",
        help="Path to the project that should be scanned.",
    )

    parser.add_argument(
        "--output",
        help="Optional path for the JSON report.",
    )

    args = parser.parse_args()

    try:
        findings = scan_project(args.project_directory)
        report = build_report(
            args.project_directory,
            findings,
        )
    except (FileNotFoundError, NotADirectoryError) as error:
        parser.error(str(error))

    print(json.dumps(report, indent=2))

    report_path = write_report(
        args.project_directory,
        args.output,
    )

    print(f"\nSecurity report saved to: {report_path}")


if __name__ == "__main__":
    main()