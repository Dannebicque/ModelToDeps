# python
from typing import List, Optional
from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QGraphicsItem


class NodeItem(QGraphicsItem):
    def __init__(self, node_id: int, node_type: str, rect: QRectF, label: str = "",
                 color: QColor = QColor("white")):
        super().__init__()
        self.node_id = node_id
        self.node_type = node_type
        self.rect = rect
        self.label = label or ("Box" if node_type == "rect" else "Étape")
        self.color = color
        self.edges: List["EdgeItem"] = []

        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemSendsGeometryChanges
        )

    def boundingRect(self) -> QRectF:
        margin = 4
        return self.rect.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter, option, widget=None):
        pen = QPen(Qt.black, 2)
        if self.isSelected():
            pen.setColor(QColor("#007acc"))
            pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.color))

        if self.node_type == "rect":
            painter.drawRect(self.rect)
        else:
            painter.drawEllipse(self.rect)

        painter.setPen(Qt.black)
        painter.drawText(self.rect, Qt.AlignCenter, self.label)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edges:
                edge.updatePosition()
        return super().itemChange(change, value)

    def center(self) -> QPointF:
        return self.mapToScene(self.rect.center())
