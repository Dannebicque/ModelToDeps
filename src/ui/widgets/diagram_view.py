# ui/widgets/diagram_view.py (compléments)
from __future__ import annotations

from typing import Optional, Callable, Dict

from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsLineItem,
    QGraphicsItem,
)
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QWheelEvent
from PySide6.QtCore import Qt, QPointF

from domain.models.diagram import Diagram


class DiagramView(QGraphicsView):
    def __init__(self, on_changed: Optional[Callable[[], None]] = None, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.diagram: Optional[Diagram] = None
        self.on_changed = on_changed or (lambda: None)
        self.node_items = {}
        self.connection_items = {}

        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self._zoom = 1.0

    def wheelEvent(self, event: QWheelEvent):
        # Ctrl + molette = zoom
        if event.modifiers() & Qt.ControlModifier:
            angle = event.angleDelta().y()
            factor = 1.15 if angle > 0 else 1 / 1.15
            self._apply_zoom(factor)
        else:
            super().wheelEvent(event)

    def _apply_zoom(self, factor: float):
        self._zoom *= factor
        self.scale(factor, factor)

    def zoom_in(self):
        self._apply_zoom(1.15)

    def zoom_out(self):
        self._apply_zoom(1 / 1.15)

    def reset_view(self):
        self.resetTransform()
        self._zoom = 1.0
        if self.scene.items():
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def center_on_diagram(self):
        if self.scene.items():
            self.centerOn(self.scene.itemsBoundingRect().center())

    def set_diagram(self, diagram: "Diagram | None") -> None:
        """
        Assigne un Diagram à la vue, réinitialise la scène et recrée
        les Node/Connection items à partir des données du diagramme.
        """
        # garder la référence
        self.diagram = diagram

        # vider la scène et les maps d'items
        if hasattr(self, "scene") and self.scene is not None:
            self.scene.clear()
        self.node_items.clear()
        self.connection_items.clear()

        if not diagram:
            return

        # recréer les nodes puis les connections (ordre important si add_connection
        # s'appuie sur des NodeItems existants)
        for node in getattr(diagram, "nodes", []):
            # suppose que add_node existe et gère la création / mapping
            try:
                self.add_node(node)
            except Exception:
                # éviter de planter si add_node n'est pas encore implémentée
                pass

        for conn in getattr(diagram, "connections", []):
            try:
                self.add_connection(conn)
            except Exception:
                pass

        # repositionner / réinitialiser la vue si méthode fournie
        if hasattr(self, "reset_view"):
            try:
                self.reset_view()
            except Exception:
                pass
