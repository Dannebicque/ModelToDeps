from dataclasses import dataclass, field
from typing import Dict, List
from .diagram import Diagram, DiagramType
import uuid


@dataclass
class StepData:
    """Données propres à une étape du wizard : diagrammes + paramètres."""

    id: str
    name: str
    description: str = ""
    diagrams: List[Diagram] = field(default_factory=list)
    settings: Dict[str, str] = field(default_factory=dict)  # petites options locales


@dataclass
class Project:
    id: str
    name: str
    description: str = ""
    version: str = "1.0"
    steps: Dict[str, StepData] = field(default_factory=dict)

    @staticmethod
    def create(name: str, description: str = "") -> "Project":
        project_id = str(uuid.uuid4())
        # Initialiser les 6 étapes avec des ids stables
        steps = {
            "step_01_archi": StepData(id="step_01_archi", name="Architecture"),
            "step_02_signaux": StepData(id="step_02_signaux", name="Signaux / IO"),
            "step_03_logic": StepData(id="step_03_logic", name="Logique"),
            "step_04_safety": StepData(id="step_04_safety", name="Sécurité"),
            "step_05_sequences": StepData(id="step_05_sequences", name="Séquences"),
            "step_06_summary": StepData(id="step_06_summary", name="Synthèse"),
        }
        return Project(id=project_id, name=name, description=description, steps=steps)
