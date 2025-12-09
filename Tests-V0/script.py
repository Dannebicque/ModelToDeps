import json
import sys
from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtCore import (
    Qt,
    QRectF,
    QPointF,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPainterPath,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QColorDialog,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QFileDialog,
    QInputDialog,
    QMessageBox,
)


@dataclass
class NodeData:
    id: int
    node_type: str  # "rect" ou "oval"
    x: float
    y: float
    width: float
    height: float
    label: str
    color: str  # "#RRGGBB"


@dataclass
class EdgeData:
    source_id: int
    target_id: int
    color: str  # "#RRGGBB"


class NodeItem(QGraphicsItem):
    """
    Un node : rectangle ou ellipse + texte centré.
    """

    def __init__(self, node_id: int, node_type: str, rect: QRectF, label: str = "",
                 color: QColor = QColor("white"), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node_id = node_id
        self.node_type = node_type  # "rect" ou "oval"
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
        # On ajoute un peu de marge pour le stroke & le texte
        margin = 4
        return self.rect.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter, option, widget=None):
        # Shape
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

        # Texte centré
        painter.setPen(Qt.black)
        painter.drawText(self.rect, Qt.AlignCenter, self.label)

    def itemChange(self, change, value):
        # Quand la position change, on met à jour les arêtes reliées
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edges:
                edge.updatePosition()
        return super().itemChange(change, value)

    def center(self) -> QPointF:
        return self.mapToScene(self.rect.center())


class EdgeItem(QGraphicsItem):
    """
    Flèche orientée entre deux NodeItem (source -> target).
    """

    def __init__(self, source: NodeItem, target: NodeItem,
                 color: QColor = QColor("black"), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source = source
        self.target = target
        self.color = color

        # On enregistre la liaison dans les nodes
        self.source.edges.append(self)
        self.target.edges.append(self)

        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)  # Derrière les nodes

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

        # Ligne principale
        painter.drawPath(self._path)

        # Dessiner la pointe de flèche côté cible
        src = self.source.center()
        tgt = self.target.center()
        # vecteur
        dx = tgt.x() - src.x()
        dy = tgt.y() - src.y()
        length = (dx ** 2 + dy ** 2) ** 0.5 or 1
        ux, uy = dx / length, dy / length

        arrow_size = 10
        # point sur la ligne un peu avant la cible
        px = tgt.x() - ux * arrow_size
        py = tgt.y() - uy * arrow_size

        # vecteur normal
        nx, ny = -uy, ux
        p1 = QPointF(px + nx * arrow_size * 0.5, py + ny * arrow_size * 0.5)
        p2 = QPointF(px - nx * arrow_size * 0.5, py - ny * arrow_size * 0.5)

        arrow_path = QPainterPath()
        arrow_path.moveTo(tgt)
        arrow_path.lineTo(p1)
        arrow_path.lineTo(p2)
        arrow_path.closeSubpath()

        painter.setBrush(self.color if not self.isSelected() else QColor("#007acc"))
        painter.drawPath(arrow_path)

    def reverseDirection(self):
        # Inverse source et target
        self.source.edges.remove(self)
        self.target.edges.remove(self)
        self.source, self.target = self.target, self.source
        self.source.edges.append(self)
        self.target.edges.append(self)
        self.updatePosition()


class DiagramScene(QGraphicsScene):
    """
    Scene qui gère :
    - Ajout de nodes (rect / oval) en cliquant
    - Mode connexion pour créer des flèches
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tool = "select"  # "select" | "rect" | "oval" | "connect"
        self.node_id_counter = 1
        self.connect_source: Optional[NodeItem] = None

    def setTool(self, tool: str):
        self.current_tool = tool
        self.connect_source = None

    def mousePressEvent(self, event):
        clicked_item = self.itemAt(event.scenePos(), self.views()[0].transform()) if self.views() else None

        if self.current_tool in ("rect", "oval"):
            # On n'ajoute un node que si on clique sur le fond
            if not isinstance(clicked_item, NodeItem) and not isinstance(clicked_item, EdgeItem):
                size = 120, 60
                w, h = size
                rect = QRectF(-w / 2, -h / 2, w, h)
                node = NodeItem(
                    node_id=self.node_id_counter,
                    node_type=self.current_tool,
                    rect=rect,
                    label="Box" if self.current_tool == "rect" else "Étape",
                )
                self.node_id_counter += 1
                node.setPos(event.scenePos())
                self.addItem(node)
                self.clearSelection()
                node.setSelected(True)
                return  # On ne laisse pas QGraphicsScene gérer plus
        elif self.current_tool == "connect":
            # Mode connexion : clic sur un NodeItem -> source, puis second clic -> target
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

        # sinon comportement normal (sélection / drag)
        super().mousePressEvent(event)

    def to_json(self) -> str:
        nodes_data: List[NodeData] = []
        edges_data: List[EdgeData] = []

        for item in self.items():
            if isinstance(item, NodeItem):
                center = item.pos()
                nodes_data.append(
                    NodeData(
                        id=item.node_id,
                        node_type=item.node_type,
                        x=center.x(),
                        y=center.y(),
                        width=item.rect.width(),
                        height=item.rect.height(),
                        label=item.label,
                        color=item.color.name(),
                    )
                )

        # Pour éviter les doublons, on ne parcourt que les EdgeItem
        for item in self.items():
            if isinstance(item, EdgeItem):
                edges_data.append(
                    EdgeData(
                        source_id=item.source.node_id,
                        target_id=item.target.node_id,
                        color=item.color.name(),
                    )
                )

        data = {
            "nodes": [n.__dict__ for n in nodes_data],
            "edges": [e.__dict__ for e in edges_data],
        }
        return json.dumps(data, indent=2)

    def load_json(self, text: str):
        data = json.loads(text)
        self.clear()
        self.node_id_counter = 1

        id_to_node = {}

        # Nodes
        for n in data.get("nodes", []):
            rect = QRectF(-n["width"] / 2, -n["height"] / 2, n["width"], n["height"])
            node = NodeItem(
                node_id=n["id"],
                node_type=n["node_type"],
                rect=rect,
                label=n.get("label", ""),
                color=QColor(n.get("color", "#ffffff")),
            )
            node.setPos(QPointF(n["x"], n["y"]))
            self.addItem(node)
            id_to_node[n["id"]] = node
            self.node_id_counter = max(self.node_id_counter, n["id"] + 1)

        # Edges
        for e in data.get("edges", []):
            s = id_to_node.get(e["source_id"])
            t = id_to_node.get(e["target_id"])
            if s and t:
                edge = EdgeItem(s, t, color=QColor(e.get("color", "#000000")))
                self.addItem(edge)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Éditeur de schémas - Python / Qt")
        self.resize(1000, 700)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        # Sidebar
        sidebar = QVBoxLayout()
        main_layout.addLayout(sidebar, 0)

        self.btn_rect = QPushButton("Ajouter une box (rectangle)")
        self.btn_oval = QPushButton("Ajouter une étape (ovale)")
        self.btn_connect = QPushButton("Relier (flèche)")
        self.btn_select = QPushButton("Sélection / déplacement")

        sidebar.addWidget(self.btn_rect)
        sidebar.addWidget(self.btn_oval)
        sidebar.addWidget(self.btn_connect)
        sidebar.addWidget(self.btn_select)

        self.btn_color = QPushButton("Changer la couleur de l'élément sélectionné")
        sidebar.addWidget(self.btn_color)

        self.btn_edit_text = QPushButton("Éditer le texte de la forme sélectionnée")
        sidebar.addWidget(self.btn_edit_text)

        sidebar.addSpacing(10)

        self.btn_export = QPushButton("Exporter en JSON (fichier)")
        self.btn_import = QPushButton("Importer depuis JSON (fichier)")
        sidebar.addWidget(self.btn_export)
        sidebar.addWidget(self.btn_import)

        sidebar.addStretch()

        # Graphics view
        self.scene = DiagramScene(self)
        self.scene.setSceneRect(-500, -500, 1000, 1000)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints())
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        main_layout.addWidget(self.view, 1)

        # Connections
        self.btn_rect.clicked.connect(lambda: self.setTool("rect"))
        self.btn_oval.clicked.connect(lambda: self.setTool("oval"))
        self.btn_connect.clicked.connect(lambda: self.setTool("connect"))
        self.btn_select.clicked.connect(lambda: self.setTool("select"))

        self.btn_color.clicked.connect(self.changeColorOfSelection)
        self.btn_edit_text.clicked.connect(self.editTextOfSelection)

        self.btn_export.clicked.connect(self.exportJsonToFile)
        self.btn_import.clicked.connect(self.importJsonFromFile)

        self.setTool("select")

    def setTool(self, tool: str):
        self.scene.setTool(tool)
        # simple feedback visuel
        for btn in (self.btn_rect, self.btn_oval, self.btn_connect, self.btn_select):
            btn.setStyleSheet("")
        if tool == "rect":
            self.btn_rect.setStyleSheet("background:#007acc;color:white;")
        elif tool == "oval":
            self.btn_oval.setStyleSheet("background:#007acc;color:white;")
        elif tool == "connect":
            self.btn_connect.setStyleSheet("background:#007acc;color:white;")
        else:
            self.btn_select.setStyleSheet("background:#007acc;color:white;")

    def getSelectedItem(self):
        selected = self.scene.selectedItems()
        if not selected:
            return None
        # On prend le premier (tu pourrais gérer multi-sélection plus tard)
        return selected[0]

    def changeColorOfSelection(self):
        item = self.getSelectedItem()
        if item is None:
            QMessageBox.information(self, "Couleur", "Aucun élément sélectionné.")
            return

        color = QColorDialog.getColor(parent=self, title="Choisir une couleur")
        if not color.isValid():
            return

        if isinstance(item, NodeItem):
            item.color = color
            item.update()
        elif isinstance(item, EdgeItem):
            item.color = color
            item.update()

    def editTextOfSelection(self):
        item = self.getSelectedItem()
        if item is None or not isinstance(item, NodeItem):
            QMessageBox.information(self, "Texte", "Sélectionne d'abord une forme (rectangle ou ovale).")
            return

        text, ok = QInputDialog.getText(self, "Texte de la forme",
                                        "Texte :", text=item.label)
        if ok:
            item.label = text
            item.update()

    def exportJsonToFile(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter le diagramme en JSON", "", "JSON (*.json)"
        )
        if not path:
            return
        text = self.scene.to_json()
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        QMessageBox.information(self, "Export", f"Diagramme exporté dans {path}")

    def importJsonFromFile(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importer un diagramme JSON", "", "JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            self.scene.load_json(text)
        except Exception as e:
            QMessageBox.critical(self, "Import", f"Erreur lors de l'import : {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
