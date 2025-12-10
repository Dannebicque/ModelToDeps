"""Vue graphique pour afficher les diagrammes."""

from __future__ import annotations

from typing import Optional, Callable, Dict, Iterable

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QWheelEvent, QPainterPath
from PySide6.QtCore import Qt, QPointF, QRectF

from domain.models.diagram import Diagram, Connection, Node, NodeAppearance, NodeShape, BorderStyle


NODE_WIDTH = 140
NODE_HEIGHT = 70


class NodeGraphicsItem(QGraphicsItem):
    def __init__(
        self,
        node: Node,
        on_moved: Callable[["NodeGraphicsItem"], None],
    ):
        super().__init__()
        self.node = node
        self.on_moved = on_moved
        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(1)

    def boundingRect(self) -> QRectF:
        margin = 6
        return QRectF(-NODE_WIDTH / 2 - margin, -NODE_HEIGHT / 2 - margin, NODE_WIDTH + 2 * margin, NODE_HEIGHT + 2 * margin)

    def paint(self, painter: QPainter, option, widget=None):
        appearance: NodeAppearance = self.node.appearance
        pen = QPen(QColor(appearance.border_color))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(appearance.fill_color)))

        rect = QRectF(-NODE_WIDTH / 2, -NODE_HEIGHT / 2, NODE_WIDTH, NODE_HEIGHT)

        if appearance.shape == NodeShape.ELLIPSE:
            painter.drawEllipse(rect)
            if appearance.border == BorderStyle.DOUBLE:
                inset = 6
                painter.drawEllipse(rect.adjusted(inset, inset, -inset, -inset))
        else:
            painter.drawRoundedRect(rect, 8, 8)
            if appearance.border == BorderStyle.DOUBLE:
                inset = 6
                painter.drawRoundedRect(rect.adjusted(inset, inset, -inset, -inset), 8, 8)

        # libellé
        painter.setPen(QPen(QColor(appearance.text_color)))
        painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, self.node.label)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.on_moved(self)
        return super().itemChange(change, value)

    def center(self) -> QPointF:
        return self.scenePos()


class ArrowItem(QGraphicsItem):
    def __init__(self, source: NodeGraphicsItem, target: NodeGraphicsItem):
        super().__init__()
        self.source = source
        self.target = target
        self.setZValue(0)
        self.pen = QPen(QColor("#555"))
        self.pen.setWidth(2)

    def boundingRect(self) -> QRectF:
        p1 = self.source.center()
        p2 = self.target.center()
        return QRectF(p1, p2).normalized().adjusted(-10, -10, 10, 10)

    def paint(self, painter: QPainter, option, widget=None):
        p1 = self.source.center()
        p2 = self.target.center()
        painter.setPen(self.pen)
        painter.drawLine(p1, p2)

        # flèche
        line = p2 - p1
        if line.manhattanLength() == 0:
            return
        angle = line.angle()
        arrow_size = 10
        direction = QPointF.fromPolar(arrow_size, angle + 30)
        direction2 = QPointF.fromPolar(arrow_size, angle - 30)
        path = QPainterPath()
        path.moveTo(p2)
        path.lineTo(p2 - direction)
        path.moveTo(p2)
        path.lineTo(p2 - direction2)
        painter.drawPath(path)


class DiagramView(QGraphicsView):
    def __init__(self, on_changed: Optional[Callable[[], None]] = None, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.diagram: Optional[Diagram] = None
        self.on_changed = on_changed or (lambda: None)
        self.node_items: Dict[str, NodeGraphicsItem] = {}
        self.connection_items: Dict[str, ArrowItem] = {}

        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self._zoom = 1.0

    def wheelEvent(self, event: QWheelEvent):
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
        self.diagram = diagram
        self.scene.clear()
        self.node_items.clear()
        self.connection_items.clear()

        if not diagram:
            return

        for node in getattr(diagram, "nodes", []):
            self.add_node(node)

        for conn in getattr(diagram, "connections", []):
            self.add_connection(conn)

        self.reset_view()

    # -- Node management --
    def add_node(self, node: Node) -> None:
        def on_moved(item: NodeGraphicsItem):
            node.x = item.scenePos().x()
            node.y = item.scenePos().y()
            self._refresh_connections_for(node.id)
            self.on_changed()

        item = NodeGraphicsItem(node=node, on_moved=on_moved)
        item.setPos(QPointF(node.x, node.y))
        self.scene.addItem(item)
        self.node_items[node.id] = item

    def get_selected_node_ids(self) -> Iterable[str]:
        for node_id, item in self.node_items.items():
            if item.isSelected():
                yield node_id

    # -- Connections --
    def add_connection(self, connection: Connection) -> None:
        source_item = self.node_items.get(connection.source_id)
        target_item = self.node_items.get(connection.target_id)
        if not source_item or not target_item:
            return
        arrow = ArrowItem(source_item, target_item)
        self.scene.addItem(arrow)
        self.connection_items[connection.id] = arrow
        self.on_changed()

    def _refresh_connections_for(self, node_id: str):
        for conn_id, arrow in self.connection_items.items():
            if (
                arrow.source.node.id == node_id
                or arrow.target.node.id == node_id
            ):
                arrow.update()

