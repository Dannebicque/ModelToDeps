from pathlib import Path
from typing import Any, Dict, List

from domain.models.project import Project, StepData
from domain.models.diagram import (
    Diagram,
    Node,
    Connection,
    DiagramType,
    NodeType,
    NodeAppearance,
    ConnectionType,
)
from infrastructure.storage.file_storage import FileStorage


class ProjectRepository:
    def __init__(self):
        self.storage = FileStorage()

    def _project_to_dict(self, project: Project) -> Dict[str, Any]:
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "version": project.version,
            "steps": {
                step_id: {
                    "id": step.id,
                    "name": step.name,
                    "description": step.description,
                    "settings": step.settings,
                    "diagrams": [
                        {
                            "id": d.id,
                            "name": d.name,
                            "diagram_type": d.diagram_type.value,
                            "nodes": [
                                {
                                    "id": n.id,
                                    "type": n.type.value,
                                    "label": n.label,
                                    "x": n.x,
                                    "y": n.y,
                                    "appearance": n.appearance.to_dict(),
                                    "properties": n.properties,
                                }
                                for n in d.nodes
                            ],
                            "connections": [
                                {
                                    "id": c.id,
                                    "source_id": c.source_id,
                                    "target_id": c.target_id,
                                    "label": c.label,
                                    "type": c.type.value,
                                }
                                for c in d.connections
                            ],
                        }
                        for d in step.diagrams
                    ],
                }
                for step_id, step in project.steps.items()
            },
        }

    def _project_from_dict(self, data: Dict[str, Any]) -> Project:
        steps: Dict[str, StepData] = {}
        for step_id, s in data.get("steps", {}).items():
            diagrams: List[Diagram] = []
            for d in s.get("diagrams", []):
                nodes = [
                    Node(
                        id=n["id"],
                        type=NodeType(n["type"]),
                        label=n["label"],
                        x=n["x"],
                        y=n["y"],
                        appearance=NodeAppearance.from_dict(n.get("appearance")),
                        properties=n.get("properties", {}),
                    )
                    for n in d.get("nodes", [])
                ]
                conns = [
                    Connection(
                        id=c["id"],
                        source_id=c["source_id"],
                        target_id=c["target_id"],
                        label=c.get("label", ""),
                        type=ConnectionType(c.get("type", ConnectionType.DEFAULT.value)),
                    )
                    for c in d.get("connections", [])
                ]
                diagrams.append(
                    Diagram(
                        id=d["id"],
                        name=d["name"],
                        diagram_type=DiagramType(d.get("diagram_type", "other")),
                        nodes=nodes,
                        connections=conns,
                    )
                )

            steps[step_id] = StepData(
                id=s["id"],
                name=s["name"],
                description=s.get("description", ""),
                settings=s.get("settings", {}),
                diagrams=diagrams,
            )

        project = Project(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
            steps=steps,
        )
        return project

    def save(self, project: Project, path: Path) -> None:
        payload = self._project_to_dict(project)
        self.storage.write_json(path, payload)

    def load(self, path: Path) -> Project:
        data = self.storage.read_json(path)
        return self._project_from_dict(data)
