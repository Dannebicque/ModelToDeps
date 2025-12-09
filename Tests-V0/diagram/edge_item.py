# python
from PySide6.QtCore import QPointF, Qt, QRectF
from PySide6.QtGui import QPainterPath, QPen, QColor
from PySide6.QtWidgets import QGraphicsItem


class EdgeItem(QGraphicsItem):
    def __init__(self, source: "NodeItem", target: "NodeItem", color: QColor = QColor("black")):
        super().__init__()
        self.source = source
        self.target = target
        self.color = color

        self.source.edges.append(self)
        self.target.edges.append(self)

        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

        self._path = QPainterPath()
        self.updatePosition()

    def boundingRect(self) -> QRectF:
        return self._path.boundingRect().adjusted(-4, -4, 4, 4)

    def updatePosition(self):
        src = self.source.center()
        tgt = self.target.center()
        path = QPainterPath()
        path.moveTo(src)
        path.lineTo(tgt)
        self.prepareGeometryChange()
        self._path = path

    def paint(self, painter, option, widget=None):
        pen = QPen(self.color, 2)
        if self.isSelected():
            pen.setColor(QColor("#007acc"))
            pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self._path)

        # simple arrow head
        src = self.source.center()
        tgt = self.target.center()
        dx = tgt.x() - src.x()
        dy = tgt.y() - src.y()
        length = (dx ** 2 + dy ** 2) ** 0.5 or 1
        ux, uy = dx / length, dy / length
        arrow_size = 10
        px = tgt.x() - ux * arrow_size
        py = tgt.y() - uy * arrow_size
        nx, ny = -uy, ux
        p1 = QPointF(px + nx * arrow_size * 0.5, py + ny * arrow_size * 0.5)
        p2 = QPointF(px - nx * arrow_size * 0.5, py - ny * arrow_size * 0.5)

        arrow = QPainterPath()
        arrow.moveTo(tgt)
        arrow.lineTo(p1)
        arrow.lineTo(p2)
        arrow.closeSubpath()

        painter.setBrush(self.color if not self.isSelected() else QColor("#007acc"))
        painter.drawPath(arrow)

    def reverseDirection(self):
        self.source.edges.remove(self)
        self.target.edges.remove(self)
        self.source, self.target = self.target, self.source
        self.source.edges.append(self)
        self.target.edges.append(self)
        self.updatePosition()
