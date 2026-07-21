import re

from src.models.schemas import ProjectPlan


FEATURE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "User authentication": (
        "authentication",
        "login",
        "signup",
        "sign up",
        "user account",
    ),
    "Role-based access control": (
        "admin",
        "roles",
        "permissions",
        "role-based",
    ),
    "Payment processing": (
        "payment",
        "checkout",
        "stripe",
        "subscription",
        "billing",
    ),
    "Search and filtering": (
        "search",
        "filter",
        "sorting",
    ),
    "File uploads": (
        "upload",
        "document",
        "image upload",
        "file storage",
    ),
    "Notifications": (
        "notification",
        "email alert",
        "sms",
        "push notification",
    ),
    "Analytics dashboard": (
        "analytics",
        "dashboard",
        "reporting",
        "metrics",
    ),
    "Real-time communication": (
        "chat",
        "real-time",
        "realtime",
        "websocket",
    ),
    "REST API": (
        "api",
        "rest",
        "endpoint",
    ),
}


def _slugify(value: str) -> str:
    """Convert text into a safe project-directory name."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    return value.strip("-") or "generated-application"


def _generate_project_name(requirement: str) -> str:
    ignored_words = {
        "a",
        "an",
        "the",
        "build",
        "create",
        "develop",
        "make",
        "application",
        "app",
        "website",
        "platform",
        "system",
        "with",
        "for",
    }

    words = re.findall(r"[A-Za-z0-9]+", requirement)
    meaningful_words = [
        word for word in words if word.lower() not in ignored_words
    ]

    selected_words = meaningful_words[:4] or ["agentforge", "project"]
    return _slugify("-".join(selected_words))


def _detect_application_type(text: str) -> str:
    application_types = {
        "E-commerce application": ("ecommerce", "e-commerce", "shopping store"),
        "Booking application": ("booking", "reservation", "appointment"),
        "AI application": ("ai", "llm", "rag", "machine learning", "chatbot"),
        "Social application": ("social network", "community", "social media"),
        "Dashboard application": ("dashboard", "analytics", "reporting"),
        "Content management application": ("blog", "cms", "content management"),
        "Task management application": ("task manager", "project management", "kanban"),
    }

    for application_type, keywords in application_types.items():
        if any(keyword in text for keyword in keywords):
            return application_type

    return "General web application"


def _detect_frontend(text: str) -> str:
    if "next.js" in text or "nextjs" in text:
        return "Next.js"
    if "react" in text:
        return "React"
    if "streamlit" in text:
        return "Streamlit"
    if "vue" in text:
        return "Vue.js"
    if "angular" in text:
        return "Angular"

    return "React"


def _detect_backend(text: str) -> str:
    if "django" in text:
        return "Django"
    if "flask" in text:
        return "Flask"
    if "node.js" in text or "nodejs" in text or "express" in text:
        return "Node.js with Express"
    if "fastapi" in text:
        return "FastAPI"

    return "FastAPI"


def _detect_database(text: str) -> str:
    if "postgresql" in text or "postgres" in text:
        return "PostgreSQL"
    if "mongodb" in text or "mongo" in text:
        return "MongoDB"
    if "mysql" in text:
        return "MySQL"
    if "sqlite" in text:
        return "SQLite"

    return "SQLite"


def _detect_features(text: str) -> list[str]:
    features = []

    for feature, keywords in FEATURE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            features.append(feature)

    if not features:
        features.append("Core CRUD operations")

    return features


def _generate_warnings(features: list[str]) -> list[str]:
    warnings = []

    if "Payment processing" in features:
        warnings.append(
            "Payment data must be handled through a PCI-compliant provider."
        )

    if "User authentication" in features:
        warnings.append(
            "Passwords must be hashed and secrets must not be committed to Git."
        )

    if "File uploads" in features:
        warnings.append(
            "Uploaded files require type, size, and malware validation."
        )

    return warnings


def plan_project(requirement: str) -> ProjectPlan:
    """Convert a natural-language requirement into a structured project plan."""
    requirement = requirement.strip()

    if not requirement:
        raise ValueError("Project requirement cannot be empty.")

    normalized_text = requirement.lower()
    features = _detect_features(normalized_text)

    return ProjectPlan(
        project_name=_generate_project_name(requirement),
        summary=requirement,
        application_type=_detect_application_type(normalized_text),
        frontend=_detect_frontend(normalized_text),
        backend=_detect_backend(normalized_text),
        database=_detect_database(normalized_text),
        features=features,
        folders=[
            "frontend",
            "backend",
            "tests",
            "docs",
        ],
        warnings=_generate_warnings(features),
    )