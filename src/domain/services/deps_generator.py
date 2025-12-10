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
                    eq = node.properties.get("equation", "")
                    style = node.appearance
                    style_tokens = [
                        f"shape={style.shape.value}",
                        f"border={style.border.value}",
                        f"fill={style.fill_color}",
                        f"stroke={style.border_color}",
                    ]
                    properties_tokens = [f"{k}={v}" for k, v in node.properties.items() if k != "equation"]
                    payload = " ".join(style_tokens + properties_tokens)
                    if eq:
                        payload = f"{payload} EQUATION '{eq}'".strip()
                    lines.append(
                        f"NODE {node.id} {node.type.value} {node.label} {payload}".strip()
                    )
            lines.append("")

        return "\n".join(lines)
