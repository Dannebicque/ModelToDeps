"""Vue graphique pour afficher les diagrammes."""

from __future__ import annotations

from typing import Optional, Callable, Dict, Iterable, Any
from uuid import uuid4

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PySide6.QtGui import (
    QPen,
    QBrush,
    QColor,
    QPainter,
    QWheelEvent,
    QPainterPath,
    QDropEvent,
)
from PySide6.QtCore import Qt, QPointF, QRectF, QMimeData, QEvent

from domain.models.diagram import (
    Diagram,
    Connection,
    Node,
    NodeAppearance,
    NodeShape,
    BorderStyle,
    NodeType,
    ConnectionType,
)


NODE_WIDTH = 140
NODE_HEIGHT = 70
COMPONENT_MIME_TYPE = "application/x-diagram-component"

CONNECTION_COLORS: dict[ConnectionType, str] = {
    ConnectionType.DEFAULT: "#555555",
    ConnectionType.FLOW: "#0d99ff",
    ConnectionType.CONDITION: "#f5a524",
    ConnectionType.FEEDBACK: "#7b61ff",
}


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
    def __init__(
        self,
        source: NodeGraphicsItem,
        target: NodeGraphicsItem,
        connection_type: ConnectionType = ConnectionType.DEFAULT,
    ):
        super().__init__()
        self.source = source
        self.target = target
        self.setZValue(0)
        color = CONNECTION_COLORS.get(connection_type, CONNECTION_COLORS[ConnectionType.DEFAULT])
        self.pen = QPen(QColor(color))
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

        self._add_component_callback: Optional[Callable[[str, QPointF], None]] = None
        self._active_component_id: Optional[str] = None

        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.viewport().installEventFilter(self)

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

    def set_component_adder(self, callback: Callable[[str, QPointF], None]):
        self._add_component_callback = callback

    def set_active_component(self, component_id: str | None):
        self._active_component_id = component_id

    def set_diagram(self, diagram: "Diagram | None") -> None:
        self.diagram = diagram
        self.scene.clear()
        self.node_items.clear()
        self.connection_items.clear()

        if not diagram:
            return

        normalized_nodes = []
        for node in getattr(diagram, "nodes", []):
            normalized = self._normalize_node(node)
            if normalized:
                normalized_nodes.append(normalized)
                self.add_node(normalized)
        diagram.nodes = normalized_nodes

        normalized_connections = []
        for conn in getattr(diagram, "connections", []):
            normalized = self._normalize_connection(conn)
            if normalized:
                normalized_connections.append(normalized)
                self.add_connection(normalized)
        diagram.connections = normalized_connections

        self.reset_view()

    def _normalize_node(self, node: Any) -> Optional[Node]:
        if isinstance(node, Node):
            return node

        if isinstance(node, dict):
            try:
                node_id = str(node.get("id", uuid4()))
                node_type_raw = node.get("type", NodeType.ACTION.value)
                node_type = node_type_raw if isinstance(node_type_raw, NodeType) else NodeType(node_type_raw)
                return Node(
                    id=node_id,
                    type=node_type,
                    label=str(node.get("label", "")),
                    x=float(node.get("x", 0)),
                    y=float(node.get("y", 0)),
                    appearance=NodeAppearance.from_dict(node.get("appearance")),
                    properties=node.get("properties", {}),
                )
            except Exception as exc:  # pragma: no cover - defensive
                print(f"[DiagramView] Impossible de normaliser le node {node!r}: {exc}")
                return None

        print(f"[DiagramView] Noeud ignoré car invalide: {node!r}")
        return None

    def _normalize_connection(self, connection: Any) -> Optional[Connection]:
        if isinstance(connection, Connection):
            return connection

        if isinstance(connection, dict):
            try:
                return Connection(
                    id=str(connection.get("id", uuid4())),
                    source_id=str(connection["source_id"]),
                    target_id=str(connection["target_id"]),
                    label=str(connection.get("label", "")),
                    type=ConnectionType(connection.get("type", ConnectionType.DEFAULT.value)),
                )
            except Exception as exc:  # pragma: no cover - defensive
                print(f"[DiagramView] Impossible de normaliser la connexion {connection!r}: {exc}")
                return None

        print(f"[DiagramView] Connexion ignorée car invalide: {connection!r}")
        return None

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
        arrow = ArrowItem(source_item, target_item, connection.type)
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

    # -- Interactions --
    def _can_accept_drop(self, mime_data: QMimeData) -> bool:
        return mime_data.hasFormat(COMPONENT_MIME_TYPE) and self._add_component_callback is not None

    def _accept_drag_event(self, event: QDropEvent) -> bool:
        if not self._can_accept_drop(event.mimeData()):
            return False
        event.acceptProposedAction()
        return True

    def _handle_drop(self, event: QDropEvent) -> None:
        if not self._can_accept_drop(event.mimeData()):
            return

        component_id = bytes(event.mimeData().data(COMPONENT_MIME_TYPE)).decode()
        position = self.mapToScene(event.position().toPoint())
        if self._add_component_callback and component_id:
            self._add_component_callback(component_id, position)
        event.acceptProposedAction()

    def eventFilter(self, watched, event):  # noqa: D401
        if watched is self.viewport():
            if event.type() in (QEvent.DragEnter, QEvent.DragMove):
                if self._accept_drag_event(event):
                    return True
            elif event.type() == QEvent.Drop:
                self._handle_drop(event)
                return True
        return super().eventFilter(watched, event)

    def dragEnterEvent(self, event):  # noqa: D401
        if not self._accept_drag_event(event):
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if not self._accept_drag_event(event):
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if self._can_accept_drop(event.mimeData()):
            self._handle_drop(event)
        else:
            super().dropEvent(event)

    def mousePressEvent(self, event):
        if (
            event.button() == Qt.LeftButton
            and self._active_component_id
            and self._add_component_callback
            and self.itemAt(event.position().toPoint()) is None
        ):
            position = self.mapToScene(event.position().toPoint())
            self._add_component_callback(self._active_component_id, position)
            event.accept()
            return
        super().mousePressEvent(event)

