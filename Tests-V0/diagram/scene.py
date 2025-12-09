# python
import json
from typing import Optional, Dict
from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsScene
from diagram.node_item import NodeItem
from diagram.edge_item import EdgeItem
from diagram.models import NodeData, EdgeData


class DiagramScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tool = "select"
        self.node_id_counter = 1
        self.connect_source: Optional[NodeItem] = None

    def setTool(self, tool: str):
        self.current_tool = tool
        self.connect_source = None

    def mousePressEvent(self, event):
        clicked_item = self.itemAt(event.scenePos(), self.views()[0].transform()) if self.views() else None

        if self.current_tool in ("rect", "oval"):
            if not isinstance(clicked_item, (NodeItem, EdgeItem)):
                w, h = 120, 60
                rect = QRectF(-w / 2, -h / 2, w, h)
                node = NodeItem(node_id=self.node_id_counter, node_type=self.current_tool, rect=rect)
                self.node_id_counter += 1
                node.setPos(event.scenePos())
                self.addItem(node)
                self.clearSelection()
                node.setSelected(True)
                return

        if self.current_tool == "connect":
            if isinstance(clicked_item, NodeItem):
                if self.connect_source is None:
                    self.connect_source = clicked_item
                    self.clearSelection()
                    clicked_item.setSelected(True)
                else:
                    if clicked_item is not self.connect_source:
                        edge = EdgeItem(self.connect_source, clicked_item)
                        self.addItem(edge)
                        self.clearSelection()
                        edge.setSelected(True)
                    self.connect_source = None
                    return

        super().mousePressEvent(event)

    def to_json(self) -> str:
        nodes = []
        edges = []
        for item in self.items():
            if isinstance(item, NodeItem):
                p = item.pos()
                nd = NodeData(
                    id=item.node_id,
                    node_type=item.node_type,
                    x=p.x(),
                    y=p.y(),
                    width=item.rect.width(),
                    height=item.rect.height(),
                    label=item.label,
                    color=item.color.name(),
                )
                nodes.append(nd.to_dict())

            if isinstance(item, EdgeItem):
                ed = EdgeData(
                    source_id=item.source.node_id,
                    target_id=item.target.node_id,
                    color=item.color.name(),
                )
                edges.append(ed.to_dict())

        return json.dumps({"nodes": nodes, "edges": edges}, indent=2)

    def load_json(self, text: str):
        data = json.loads(text)
        self.clear()
        self.node_id_counter = 1
        id_map: Dict[int, NodeItem] = {}

        for n in data.get("nodes", []):
            rect = QRectF(-n["width"] / 2, -n["height"] / 2, n["width"], n["height"])
            node = NodeItem(node_id=n["id"], node_type=n["node_type"], rect=rect,
                            label=n.get("label", ""), color=QColor(n.get("color", "#ffffff")))
            node.setPos(QPointF(n["x"], n["y"]))
            self.addItem(node)
            id_map[n["id"]] = node
            self.node_id_counter = max(self.node_id_counter, n["id"] + 1)

        for e in data.get("edges", []):
            s = id_map.get(e["source_id"])
            t = id_map.get(e["target_id"])
            if s and t:
                edge = EdgeItem(s, t, color=QColor(e.get("color", "#000000")))
                self.addItem(edge)
