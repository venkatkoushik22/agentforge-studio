import json
import shutil
from pathlib import Path
from textwrap import dedent

from src.models.schemas import ProjectPlan


def _write_file(path: Path, content: str) -> None:
    """Create parent directories and write a UTF-8 file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        content.strip() + "\n",
        encoding="utf-8",
    )


def _backend_main(plan: ProjectPlan) -> str:
    """Generate the FastAPI backend entry point."""
    return dedent(
        f'''
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI(
            title={plan.project_name!r},
            description={plan.summary!r},
            version="0.2.0",
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


        @app.get("/")
        def root() -> dict[str, str]:
            return {{
                "message": "AgentForge generated backend is running",
                "status": "running",
            }}


        @app.get("/health")
        def health() -> dict[str, str]:
            return {{"status": "healthy"}}


        @app.get("/api/project")
        def project_info() -> dict[str, object]:
            return {{
                "name": {plan.project_name!r},
                "summary": {plan.summary!r},
                "application_type": {plan.application_type!r},
                "frontend": {plan.frontend!r},
                "backend": {plan.backend!r},
                "database": {plan.database!r},
                "features": {plan.features!r},
                "warnings": {plan.warnings!r},
                "status": "connected",
            }}
        '''
    )


def _frontend_app(plan: ProjectPlan) -> str:
    """Generate a React frontend connected to the FastAPI backend."""
    return dedent(
        '''
        import React, { useEffect, useState } from "react";

        const API_URL = "http://127.0.0.1:8000";

        function App() {
          const [project, setProject] = useState(null);
          const [error, setError] = useState("");

          useEffect(() => {
            const controller = new AbortController();

            async function loadProject() {
              try {
                const response = await fetch(
                  `${API_URL}/api/project`,
                  {
                    signal: controller.signal,
                  }
                );

                if (!response.ok) {
                  throw new Error(
                    `Backend returned status ${response.status}`
                  );
                }

                const data = await response.json();
                setProject(data);
              } catch (requestError) {
                if (requestError.name !== "AbortError") {
                  setError(requestError.message);
                }
              }
            }

            loadProject();

            return () => {
              controller.abort();
            };
          }, []);

          if (error) {
            return (
              <main>
                <h1>Backend connection failed</h1>
                <p>{error}</p>
                <p>
                  Confirm that FastAPI is running on port 8000.
                </p>
              </main>
            );
          }

          if (!project) {
            return (
              <main>
                <h1>Loading project...</h1>
              </main>
            );
          }

          return (
            <main>
              <p>
                Backend status: <strong>{project.status}</strong>
              </p>

              <h1>{project.name}</h1>
              <p>{project.summary}</p>

              <h2>Technology stack</h2>

              <ul>
                <li>Frontend: {project.frontend}</li>
                <li>Backend: {project.backend}</li>
                <li>Database: {project.database}</li>
                <li>Type: {project.application_type}</li>
              </ul>

              <h2>Planned features</h2>

              <ul>
                {project.features.map((feature) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>

              {project.warnings.length > 0 && (
                <>
                  <h2>Security notes</h2>

                  <ul>
                    {project.warnings.map((warning) => (
                      <li key={warning}>{warning}</li>
                    ))}
                  </ul>
                </>
              )}
            </main>
          );
        }

        export default App;
        '''
    )


def _readme(plan: ProjectPlan) -> str:
    """Generate the README for the generated project."""
    features = "\n".join(
        f"- {feature}" for feature in plan.features
    )

    warnings = (
        "\n".join(
            f"- {warning}" for warning in plan.warnings
        )
        or "- No warnings detected."
    )

    return dedent(
        f'''
        # {plan.project_name}

        Generated by AgentForge Studio.

        ## Description

        {plan.summary}

        ## Technology stack

        - Frontend: {plan.frontend}
        - Backend: {plan.backend}
        - Database: {plan.database}
        - Application type: {plan.application_type}

        ## Planned features

        {features}

        ## Security notes

        {warnings}

        ## Run the backend

        ```bash
        cd backend
        python -m venv .venv
        .venv\\Scripts\\python.exe -m pip install -r requirements.txt
        .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload
        ```

        ## Run the frontend

        ```bash
        cd frontend
        npm install
        npm run dev
        ```
        '''
    )


def generate_project(
    plan: ProjectPlan,
    output_root: Path | str = "generated_projects",
    overwrite: bool = False,
) -> Path:
    """Generate a runnable FastAPI and React project scaffold."""
    output_root = Path(output_root)
    project_directory = output_root / plan.project_name

    if project_directory.exists():
        if not overwrite:
            raise FileExistsError(
                f"Project already exists: {project_directory}. "
                "Use --force to replace it."
            )

        shutil.rmtree(project_directory)

    project_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    generated_files = [
        "README.md",
        "project_plan.json",
        "manifest.json",
        "backend/app/__init__.py",
        "backend/app/main.py",
        "backend/requirements.txt",
        "backend/.env.example",
        "frontend/package.json",
        "frontend/index.html",
        "frontend/src/main.jsx",
        "frontend/src/App.jsx",
        ".gitignore",
    ]

    _write_file(
        project_directory / "project_plan.json",
        json.dumps(
            plan.to_dict(),
            indent=2,
        ),
    )

    _write_file(
        project_directory / "manifest.json",
        json.dumps(
            {
                "generator": "AgentForge Studio",
                "version": "0.2.0",
                "project_name": plan.project_name,
                "frontend": plan.frontend,
                "backend": plan.backend,
                "database": plan.database,
                "generated_files": generated_files,
            },
            indent=2,
        ),
    )

    _write_file(
        project_directory / "README.md",
        _readme(plan),
    )

    _write_file(
        project_directory
        / "backend"
        / "app"
        / "__init__.py",
        "",
    )

    _write_file(
        project_directory
        / "backend"
        / "app"
        / "main.py",
        _backend_main(plan),
    )

    _write_file(
        project_directory
        / "backend"
        / "requirements.txt",
        dedent(
            '''
            fastapi>=0.115.0
            uvicorn[standard]>=0.30.0
            '''
        ),
    )

    _write_file(
        project_directory
        / "backend"
        / ".env.example",
        (
            f"APP_NAME={plan.project_name}\n"
            "DATABASE_URL=sqlite:///./app.db\n"
        ),
    )

    _write_file(
        project_directory
        / "frontend"
        / "package.json",
        json.dumps(
            {
                "name": f"{plan.project_name}-frontend",
                "private": True,
                "version": "0.2.0",
                "type": "module",
                "scripts": {
                    "dev": "vite",
                    "build": "vite build",
                    "preview": "vite preview",
                },
                "dependencies": {
                    "react": "^18.3.0",
                    "react-dom": "^18.3.0",
                },
                "devDependencies": {
                    "vite": "^5.4.0",
                },
            },
            indent=2,
        ),
    )

    _write_file(
        project_directory
        / "frontend"
        / "index.html",
        dedent(
            '''
            <!doctype html>
            <html lang="en">
              <head>
                <meta charset="UTF-8" />
                <meta
                  name="viewport"
                  content="width=device-width, initial-scale=1.0"
                />
                <title>AgentForge Application</title>
              </head>

              <body>
                <div id="root"></div>

                <script
                  type="module"
                  src="/src/main.jsx"
                ></script>
              </body>
            </html>
            '''
        ),
    )

    _write_file(
        project_directory
        / "frontend"
        / "src"
        / "main.jsx",
        dedent(
            '''
            import React from "react";
            import ReactDOM from "react-dom/client";
            import App from "./App.jsx";

            ReactDOM.createRoot(
              document.getElementById("root")
            ).render(
              <React.StrictMode>
                <App />
              </React.StrictMode>
            );
            '''
        ),
    )

    _write_file(
        project_directory
        / "frontend"
        / "src"
        / "App.jsx",
        _frontend_app(plan),
    )

    _write_file(
        project_directory / ".gitignore",
        dedent(
            '''
            .env
            .env.local
            *.db
            *.sqlite
            *.sqlite3
            __pycache__/
            *.py[cod]
            .venv/
            node_modules/
            dist/
            '''
        ),
    )

    return project_directory