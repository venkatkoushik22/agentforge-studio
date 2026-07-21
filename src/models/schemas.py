from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ProjectPlan:
    project_name: str
    summary: str
    application_type: str
    frontend: str
    backend: str
    database: str
    features: list[str] = field(default_factory=list)
    folders: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert the project plan into a JSON-serializable dictionary."""
        return asdict(self)