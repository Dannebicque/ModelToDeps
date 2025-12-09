from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationIssue:
    severity: Severity
    message: str
    step_id: Optional[str] = None
    diagram_id: Optional[str] = None
    node_id: Optional[str] = None
    equation_position: Optional[int] = None
