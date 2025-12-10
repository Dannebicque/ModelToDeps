"""Palette réutilisable de composants graphiques."""

from __future__ import annotations

from typing import List

from .diagram import (
    DiagramComponent,
    NodeAppearance,
    NodeShape,
    BorderStyle,
    NodeType,
)


def default_components() -> List[DiagramComponent]:
    """Retourne une palette de base de composants graphiques."""

    return [
        DiagramComponent(
            id="sensor_ellipse_single",
            display_name="Capteur (ellipse)",
            node_type=NodeType.SENSOR,
            appearance=NodeAppearance(
                shape=NodeShape.ELLIPSE,
                border=BorderStyle.SINGLE,
                fill_color="#e8f4ff",
                border_color="#0b79d0",
            ),
            default_properties={"role": "sensor"},
        ),
        DiagramComponent(
            id="sensor_ellipse_double",
            display_name="Capteur (ellipse double)",
            node_type=NodeType.SENSOR,
            appearance=NodeAppearance(
                shape=NodeShape.ELLIPSE,
                border=BorderStyle.DOUBLE,
                fill_color="#e8f4ff",
                border_color="#0b79d0",
            ),
            default_properties={"role": "sensor"},
        ),
        DiagramComponent(
            id="task_rect_single",
            display_name="Tâche (rectangle)",
            node_type=NodeType.TASK,
            appearance=NodeAppearance(
                shape=NodeShape.RECTANGLE,
                border=BorderStyle.SINGLE,
                fill_color="#f2f0ff",
                border_color="#5c4b9a",
            ),
            default_properties={"role": "task"},
        ),
        DiagramComponent(
            id="task_rect_double",
            display_name="Tâche (rectangle double)",
            node_type=NodeType.TASK,
            appearance=NodeAppearance(
                shape=NodeShape.RECTANGLE,
                border=BorderStyle.DOUBLE,
                fill_color="#f2f0ff",
                border_color="#5c4b9a",
            ),
            default_properties={"role": "task"},
        ),
        DiagramComponent(
            id="action_rect",
            display_name="Action",  # pour compatibilité avec le DEPS actuel
            node_type=NodeType.ACTION,
            appearance=NodeAppearance(
                shape=NodeShape.RECTANGLE,
                border=BorderStyle.SINGLE,
                fill_color="#f7f7f7",
                border_color="#444444",
            ),
            default_properties={},
        ),
    ]

