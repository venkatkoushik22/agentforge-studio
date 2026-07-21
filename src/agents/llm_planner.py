import os
import re
from typing import Literal

from dotenv import load_dotenv
from openai import APIError, OpenAI
from pydantic import BaseModel, Field

from src.models.schemas import ProjectPlan


load_dotenv(override=True)


class LLMProjectPlan(BaseModel):
    """Structured project plan returned by the model."""

    project_name: str = Field(
        min_length=2,
        max_length=60,
    )

    summary: str = Field(
        min_length=10,
        max_length=500,
    )

    application_type: str = Field(
        min_length=3,
        max_length=100,
    )

    database: Literal[
        "PostgreSQL",
        "SQLite",
    ]

    features: list[str] = Field(
        min_length=1,
        max_length=12,
    )

    warnings: list[str] = Field(
        default_factory=list,
        max_length=10,
    )


def _slugify(value: str) -> str:
    """Convert a project name into a safe directory name."""
    normalized = value.lower().strip()

    normalized = re.sub(
        r"[^a-z0-9\s-]",
        "",
        normalized,
    )

    normalized = re.sub(
        r"[\s_-]+",
        "-",
        normalized,
    )

    return (
        normalized.strip("-")
        or "agentforge-project"
    )


def _get_api_key() -> str:
    """Read and validate the local OpenAI API key."""
    api_key = os.getenv(
        "OPENAI_API_KEY",
        "",
    ).strip()

    invalid_values = {
        "",
        "replace_with_your_api_key",
        "replace_me",
    }

    if api_key in invalid_values:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. "
            "Add your API key to the local .env file."
        )

    return api_key


def plan_project_with_llm(
    requirement: str,
    *,
    model: str | None = None,
) -> ProjectPlan:
    """Generate a structured project plan using OpenAI."""
    requirement = requirement.strip()

    if not requirement:
        raise ValueError(
            "Project requirement cannot be empty."
        )

    selected_model = (
        model
        or os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6-luna",
        )
    )

    client = OpenAI(
        api_key=_get_api_key(),
    )

    system_prompt = """
You are the planning agent for AgentForge Studio.

Convert the user's requirement into a practical,
implementable full-stack application plan.

AgentForge currently supports:
- React frontend
- FastAPI backend
- PostgreSQL or SQLite
- REST APIs
- Security scanning
- Automated quality evaluation

Rules:
- Keep the project name short and professional.
- Choose PostgreSQL for production-style or multi-user systems.
- Choose SQLite only for small local prototypes.
- Include only features relevant to the user's request.
- Include security warnings for authentication, payments,
  file uploads, personal data, or administrative access.
- Never include credentials, passwords, or API keys.
"""

    try:
        response = client.responses.parse(
            model=selected_model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": requirement,
                },
            ],
            text_format=LLMProjectPlan,
        )
    except APIError as error:
        raise RuntimeError(
            f"OpenAI API request failed: {error}"
        ) from error

    parsed_plan = response.output_parsed

    if parsed_plan is None:
        raise RuntimeError(
            "The model did not return a valid structured plan."
        )

    return ProjectPlan(
        project_name=_slugify(
            parsed_plan.project_name
        ),
        summary=parsed_plan.summary,
        application_type=(
            parsed_plan.application_type
        ),
        frontend="React",
        backend="FastAPI",
        database=parsed_plan.database,
        features=list(
            dict.fromkeys(parsed_plan.features)
        ),
        folders=[
            "frontend",
            "backend",
            "tests",
            "docs",
        ],
        warnings=list(
            dict.fromkeys(parsed_plan.warnings)
        ),
    )