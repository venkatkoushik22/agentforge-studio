\# AgentForge Studio



\[!\[AgentForge CI](https://github.com/venkatkoushik22/agentforge-studio/actions/workflows/ci.yml/badge.svg)](https://github.com/venkatkoushik22/agentforge-studio/actions/workflows/ci.yml)

!\[Python](https://img.shields.io/badge/Python-3.12%2B-blue)

!\[LangGraph](https://img.shields.io/badge/Workflow-LangGraph-purple)

!\[FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)

!\[React](https://img.shields.io/badge/Frontend-React-blue)

!\[License](https://img.shields.io/badge/License-MIT-yellow)



\*\*AgentForge Studio\*\* is an agentic full-stack application generation system that converts natural-language requirements into tested, security-scanned, and quality-evaluated React and FastAPI project scaffolds.



Instead of only generating files, AgentForge runs each project through a structured software-engineering pipeline that includes planning, code generation, automated testing, deterministic repair, security analysis, quality evaluation, and a configurable pass/fail quality gate.



\---



\## Why AgentForge Studio?



Many code-generation tools stop after producing source files. AgentForge adds validation around the generation process.



It is designed around an evaluation-first workflow:



```text

User Requirement

&#x20;      ↓

Planning Agent

&#x20;      ↓

Project Generator

&#x20;      ↓

Automated Test Agent

&#x20;      ↓

&#x20;  Tests Passed?

&#x20;    ↙       ↘

&#x20;  No         Yes

&#x20;  ↓           ↓

Repair Agent   Security Scanner

&#x20;  ↓           ↓

Retest      Quality Evaluator

&#x20;                ↓

&#x20;            Quality Gate

&#x20;             ↙      ↘

&#x20;          Failed   Passed

```



The goal is to produce scaffolds that are not only generated, but also checked for structure, syntax, API connectivity, security risks, and overall completeness.



\---



\## Core Features



\### Natural-Language Requirement Analysis



AgentForge converts application descriptions into structured project plans containing:



\- Project name

\- Application type

\- Frontend framework

\- Backend framework

\- Database selection

\- Required features

\- Recommended folder structure

\- Security warnings



\### Free Heuristic Planner



The default planner works locally without an external API key.



It detects:



\- React, Next.js, Streamlit, Vue, and Angular references

\- FastAPI, Flask, Django, Node.js, and Express references

\- PostgreSQL, SQLite, MongoDB, and MySQL references

\- Authentication

\- Administrative access

\- Payments

\- Search and filtering

\- Notifications

\- File uploads

\- Analytics

\- Real-time communication

\- REST APIs



\### Optional LLM Planner



An optional OpenAI-powered planner can create more detailed structured plans.



The LLM planner is not required for the rest of the platform. AgentForge remains fully usable through the free heuristic planner.



\### LangGraph Orchestration



The complete generation pipeline is coordinated using LangGraph.



Workflow nodes include:



\- Planning

\- Generation

\- Testing

\- Repair

\- Security scanning

\- Quality evaluation

\- Success and failure routing



\### React and FastAPI Generation



AgentForge generates a connected full-stack scaffold containing:



\- React frontend

\- Vite development environment

\- FastAPI backend

\- CORS configuration

\- Health endpoint

\- Project metadata endpoint

\- Frontend-to-backend API connection

\- Environment variable template

\- Project manifest

\- Project-specific README



\### Automated Test Agent



Generated applications are validated for:



\- Manifest completeness

\- Required file existence

\- Backend Python syntax

\- FastAPI endpoint definitions

\- CORS configuration

\- React package configuration

\- Frontend API integration

\- Optional Vite production build



\### Automated Repair Loop



When generated-project tests fail, AgentForge can:



1\. Identify the failed checks

2\. Regenerate the scaffold from the structured plan

3\. Replace broken generated files

4\. Run the tests again

5\. Continue or fail based on the configured repair limit



The repair limit is configurable between zero and three attempts.



\### Security Scanner



The built-in scanner detects common security risks, including:



\- Hard-coded passwords

\- Hard-coded API keys

\- Hard-coded tokens and secrets

\- AWS access keys

\- Private key material

\- Python `eval` and `exec`

\- Unsafe operating-system commands

\- Subprocess calls using `shell=True`

\- JavaScript dynamic evaluation

\- Node.js command execution

\- Wildcard CORS configuration



\### Quality Evaluator



Generated applications receive a quality score based on:



\- Required file completeness

\- Backend syntax validity

\- Frontend package validity

\- Frontend-backend API contract

\- Security scan status



AgentForge can reject projects that do not meet the configured minimum score.



\### GitHub Actions CI



The repository includes continuous integration for:



\- Python source compilation

\- Unit tests on supported Python versions

\- Generated-project smoke testing

\- React dependency installation

\- Vite production builds

\- Security scanning

\- Quality evaluation

\- Report artifact uploads



\---



\## Technology Stack



| Area | Technologies |

|---|---|

| Language | Python |

| Workflow orchestration | LangGraph |

| Backend generation | FastAPI |

| Frontend generation | React, Vite |

| Databases | PostgreSQL or SQLite configuration |

| Testing | Python `unittest`, generated-project test agent |

| Security | Custom static security scanner |

| Evaluation | Rule-based quality evaluator |

| CI/CD | GitHub Actions |

| Optional AI planning | OpenAI API, Pydantic structured output |



\---



\## Installation



\### 1. Clone the repository



```bash

git clone https://github.com/venkatkoushik22/agentforge-studio.git

cd agentforge-studio

```



\### 2. Create a virtual environment



\#### Windows PowerShell



```powershell

py -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



\#### macOS or Linux



```bash

python3 -m venv .venv

source .venv/bin/activate

```



\### 3. Install the core dependencies



```bash

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

```



The core installation supports the complete free heuristic workflow.



\---



\## Quick Start



Generate an application using the free heuristic planner:



```powershell

py -m src.main "Build a React appointment booking platform using FastAPI and PostgreSQL with login, search, notifications, analytics, and admin roles" --generate --planner heuristic --skip-frontend-build

```



AgentForge will:



1\. Analyze the requirement

2\. Create a structured project plan

3\. Generate a React and FastAPI scaffold

4\. Run automated tests

5\. Repair and retest failures when necessary

6\. Scan the generated code for security risks

7\. Evaluate project quality

8\. Apply the configured quality gate



Generated applications are stored in:



```text

generated\_projects/

```



\---



\## Example Output



```text

Project generated at: generated\_projects/appointment-booking-platform

Planner used: heuristic



Automated tests

\---------------

Status: passed

Passed: 4

Failed: 0

Skipped: 1



Repair agent

\------------

Attempts used: 0

No repairs were needed.



Security scan

\-------------

Status: passed

Total findings: 0



Quality evaluation

\------------------

Status: passed

Score: 100.0%



LangGraph workflow

\------------------

Final status: passed

```



\---



\## CLI Usage



Display all supported options:



```powershell

py -m src.main --help

```



\### Main options



| Option | Description |

|---|---|

| `--generate` | Run the complete generation workflow |

| `--save` | Save only the structured project plan |

| `--force` | Replace an existing generated project |

| `--planner heuristic` | Use the free rule-based planner |

| `--planner llm` | Use the optional LLM planner |

| `--llm-model` | Override the configured LLM model |

| `--skip-frontend-build` | Skip the optional Vite production build |

| `--max-repair-attempts` | Set automatic repair attempts from 0 to 3 |

| `--skip-security-scan` | Skip security scanning |

| `--skip-evaluation` | Skip quality evaluation |

| `--minimum-score` | Set the minimum acceptable quality score |



\### Strict generation example



```powershell

py -m src.main "Build DevTrack, a React issue tracking dashboard using FastAPI and PostgreSQL with login, admin roles, search, analytics, and notifications" --generate --planner heuristic --minimum-score 90 --max-repair-attempts 2 --skip-frontend-build

```



\### Save only the project plan



```powershell

py -m src.main "Build an inventory management platform with login, search, reporting, and admin access" --save

```



\---



\## Running a Generated Application



Assume AgentForge generated:



```text

generated\_projects/my-generated-project/

```



\### Start the backend



```powershell

cd generated\_projects\\my-generated-project\\backend



py -m venv .venv



.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt



.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload

```



Backend URLs:



```text

http://127.0.0.1:8000

http://127.0.0.1:8000/health

http://127.0.0.1:8000/api/project

http://127.0.0.1:8000/docs

```



\### Start the frontend



Open another terminal:



```powershell

cd generated\_projects\\my-generated-project\\frontend



npm install



npm run dev

```



Open the Vite URL displayed in the terminal, normally:



```text

http://localhost:5173

```



The frontend retrieves live project information from the generated FastAPI backend.



\---



\## Optional LLM Planner



The LLM planner is optional and requires separate API access.



The default heuristic planner does not require payment or an API key.



\### Install optional dependencies



```bash

python -m pip install -r requirements-llm.txt

```



\### Configure environment variables



Copy the example configuration:



\#### Windows



```powershell

Copy-Item .env.example .env

```



\#### macOS or Linux



```bash

cp .env.example .env

```



Add your private configuration to `.env`:



```env

OPENAI\_API\_KEY=your\_private\_api\_key

OPENAI\_MODEL=your\_supported\_model

```



Never place a real API key in:



\- `.env.example`

\- Source code

\- GitHub commits

\- Screenshots

\- Documentation

\- Issue reports



\### Run the optional planner



```powershell

py -m src.main "Build a patient appointment platform with provider scheduling, notifications, analytics, and role-based access" --generate --planner llm

```



When API quota is unavailable, use:



```powershell

\--planner heuristic

```



\---



\## Testing



\### Run the complete repository test suite



```powershell

py -m unittest discover -s tests -p "test\_\*.py" -v

```



\### Compile the Python source



```powershell

py -m compileall -q src tests

```



\### Test an existing generated application



```powershell

py -m src.agents.tester generated\_projects\\your-project --skip-frontend-build

```



Run the Vite production-build test when frontend dependencies are installed:



```powershell

py -m src.agents.tester generated\_projects\\your-project

```



The test agent writes:



```text

test\_report.json

```



\---



\## Security Scanning



Run the scanner manually:



```powershell

py -m src.security.scanner generated\_projects\\your-project

```



The scanner writes:



```text

security\_report.json

```



Example report:



```json

{

&#x20; "status": "passed",

&#x20; "total\_findings": 0,

&#x20; "severity\_counts": {

&#x20;   "CRITICAL": 0,

&#x20;   "HIGH": 0,

&#x20;   "MEDIUM": 0,

&#x20;   "LOW": 0

&#x20; },

&#x20; "findings": \[]

}

```



\---



\## Quality Evaluation



Evaluate a generated project:



```powershell

py -m src.evaluation.evaluator generated\_projects\\your-project

```



The evaluator writes:



```text

evaluation\_report.json

```



Example:



```json

{

&#x20; "status": "passed",

&#x20; "overall\_score": 100.0,

&#x20; "passed\_checks": 5,

&#x20; "total\_checks": 5

}

```



\---



\## Generated Project Structure



A generated application contains:



```text

generated-project/

├── backend/

│   ├── app/

│   │   ├── \_\_init\_\_.py

│   │   └── main.py

│   ├── .env.example

│   └── requirements.txt

├── frontend/

│   ├── src/

│   │   ├── App.jsx

│   │   └── main.jsx

│   ├── index.html

│   └── package.json

├── .gitignore

├── README.md

├── manifest.json

├── project\_plan.json

├── test\_report.json

├── security\_report.json

└── evaluation\_report.json

```



\---



\## Repository Structure



```text

agentforge-studio/

├── .github/

│   └── workflows/

│       └── ci.yml

├── src/

│   ├── agents/

│   │   ├── generator.py

│   │   ├── planner.py

│   │   ├── llm\_planner.py

│   │   ├── tester.py

│   │   └── repairer.py

│   ├── core/

│   │   └── workflow.py

│   ├── evaluation/

│   │   └── evaluator.py

│   ├── models/

│   │   └── schemas.py

│   ├── security/

│   │   └── scanner.py

│   └── main.py

├── tests/

├── generated\_projects/

├── .env.example

├── .gitignore

├── requirements.txt

├── requirements-llm.txt

├── LICENSE

└── README.md

```



\---



\## Generated Reports



AgentForge produces machine-readable JSON artifacts for each stage:



| Report | Purpose |

|---|---|

| `project\_plan.json` | Structured interpretation of the requirement |

| `manifest.json` | Generated-file inventory |

| `test\_report.json` | Automated test results |

| `security\_report.json` | Security findings and severity counts |

| `evaluation\_report.json` | Quality score and check results |



These reports support debugging, auditing, evaluation, and future dashboard development.



\---



\## Current Limitations



AgentForge Studio is currently an MVP with the following limitations:



\- The default generated stack targets React and FastAPI.

\- Database selection currently creates configuration metadata but not complete production-ready persistence.

\- Authentication and payment features are represented in project plans but are not yet fully implemented templates.

\- The deterministic repair agent regenerates the scaffold instead of applying targeted file-level patches.

\- The static scanner is not a replacement for a complete production security review.

\- The optional LLM planner requires external API access and separate billing.

\- Generated projects may still require application-specific business logic.



These limitations are documented to keep the project technically honest and defensible.



\---



\## Roadmap



Planned improvements include:



\- SQLAlchemy model generation

\- PostgreSQL migrations

\- Authentication templates

\- Role-based access control

\- Docker and Docker Compose generation

\- Generated backend unit tests

\- Generated frontend component tests

\- Targeted file-level repair

\- LLM-assisted repair as an optional mode

\- Workflow execution dashboard

\- Run-history persistence

\- Token and latency tracking

\- Project ZIP export

\- Multiple frontend and backend templates

\- Dependency vulnerability scanning

\- Deployment templates for cloud platforms



\---



\## Design Principles



AgentForge is built around the following principles:



\### Evaluation Before Trust



Generated code should be tested and evaluated before it is treated as usable.



\### Security by Default



Generated applications should be scanned for common high-risk patterns automatically.



\### Transparent Automation



Every generation stage produces readable output and machine-readable reports.



\### Free Core Workflow



The primary workflow should remain usable without paid API access.



\### Optional AI Enhancement



External LLMs improve planning when available but are not required for the core system.



\### Reproducible Generation



A structured project plan acts as the source of truth for generation and deterministic repair.



\---



\## Author



\*\*Venkat Koushik Pillala\*\*



AI/ML Engineer focused on LLM evaluation, agentic workflows, secure application development, RAG systems, and production-oriented AI engineering.



\- GitHub: \[venkatkoushik22](https://github.com/venkatkoushik22)

\- LinkedIn: \[pillala-venkat-koushik](https://www.linkedin.com/in/pillala-venkat-koushik/)

\- Portfolio: \[personal-engineering-portfolio-hub.vercel.app](https://personal-engineering-portfolio-hub.vercel.app/)



\---



\## License



This project is licensed under the MIT License.



See the `LICENSE` file for complete terms.



\---



\## Disclaimer



AgentForge Studio generates application scaffolds intended for development, experimentation, and evaluation.



Generated projects must be reviewed, tested, secured, and adapted before production use, especially when handling authentication, payments, healthcare information, financial information, personal data, or other sensitive workloads.

