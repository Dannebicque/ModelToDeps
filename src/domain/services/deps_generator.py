from domain.models.project import Project
from domain.models.diagram import NodeType


class DepsGenerator:
    """
    Transforme le Project en texte DEPS.
    L'implémentation dépendra de ton format DEPS, ici on prépare juste la structure.
    """

    def generate(self, project: Project) -> str:
        lines: list[str] = []
        lines.append(f"# DEPS code generated for project: {project.name}")
        lines.append("# TODO: structurer selon le format DEPS réel")
        lines.append("")

        # Exemple : lister les noeuds et leurs équations
        for step_id, step in project.steps.items():
            lines.append(f"# Step: {step.name} ({step_id})")
            for diagram in step.diagrams:
                lines.append(f"# Diagram: {diagram.name}")
                for node in diagram.nodes:
                    if node.type in (NodeType.CONDITION, NodeType.ACTION):
                        eq = node.properties.get("equation", "")
                        lines.append(f"NODE {node.id} {node.type.value} {node.label} EQUATION '{eq}'")
            lines.append("")

        return "\n".join(lines)
