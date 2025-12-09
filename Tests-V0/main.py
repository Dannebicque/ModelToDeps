# python
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QColorDialog, QGraphicsView, QFileDialog, QInputDialog, QMessageBox,
     QToolBar, QToolButton, QMenu
)

from PySide6.QtGui import QAction

from diagram.scene import DiagramScene
from diagram.node_item import NodeItem
from diagram.edge_item import EdgeItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Éditeur de schémas")
        self.resize(1000, 700)

        # Menu bar classique
        file_menu = self.menuBar().addMenu("Fichier")
        act_new = QAction("Nouveau", self)
        act_open = QAction("Ouvrir...", self)
        act_exit = QAction("Quitter", self)
        file_menu.addAction(act_new)
        file_menu.addAction(act_open)
        file_menu.addSeparator()
        file_menu.addAction(act_exit)

        act_new.triggered.connect(lambda: self._info("Nouveau"))
        act_open.triggered.connect(lambda: self._info("Ouvrir"))
        act_exit.triggered.connect(self.close)

        # Toolbar
        toolbar = QToolBar("Principale", self)
        self.addToolBar(toolbar)

        # Action simple dans la toolbar
        toolbar.addAction(act_new)

        # ToolButton avec menu (comportement "vrai menu" dans la toolbar)
        tool_btn = QToolButton(self)
        tool_btn.setText("Options")
        menu = QMenu(tool_btn)
        menu.addAction("Option A", lambda: self._info("Option A"))
        menu.addAction("Option B", lambda: self._info("Option B"))
        menu.addSeparator()
        menu.addAction("Préférences...", lambda: self._info("Préférences"))

        tool_btn.setMenu(menu)
        # InstantPopup : clic ouvre immédiatement le menu (comme un menu déroulant)
        # MenuButtonPopup : clic sur la flèche ouvre le menu, clic sur le bouton peut déclencher une action
        tool_btn.setPopupMode(QToolButton.InstantPopup)

        toolbar.addWidget(tool_btn)

        def _info(self, text: str):
            QMessageBox.information(self, "Action", text)

        ## fin toolbar

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        sidebar = QVBoxLayout()
        main_layout.addLayout(sidebar, 0)

        self.btn_rect = QPushButton("Ajouter box")
        self.btn_oval = QPushButton("Ajouter étape")
        self.btn_connect = QPushButton("Relier")
        self.btn_select = QPushButton("Sélection")

        for b in (self.btn_rect, self.btn_oval, self.btn_connect, self.btn_select):
            sidebar.addWidget(b)

        self.btn_color = QPushButton("Changer couleur")
        self.btn_edit_text = QPushButton("Éditer texte")
        sidebar.addWidget(self.btn_color)
        sidebar.addWidget(self.btn_edit_text)
        sidebar.addSpacing(10)

        self.btn_export = QPushButton("Exporter JSON")
        self.btn_import = QPushButton("Importer JSON")
        sidebar.addWidget(self.btn_export)
        sidebar.addWidget(self.btn_import)
        sidebar.addStretch()

        self.scene = DiagramScene(self)
        self.scene.setSceneRect(-500, -500, 1000, 1000)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints())
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        main_layout.addWidget(self.view, 1)

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
        for btn in (self.btn_rect, self.btn_oval, self.btn_connect, self.btn_select):
            btn.setStyleSheet("")
        mapping = {"rect": self.btn_rect, "oval": self.btn_oval, "connect": self.btn_connect, "select": self.btn_select}
        mapping.get(tool, self.btn_select).setStyleSheet("background:#007acc;color:white;")

    def getSelectedItem(self):
        items = self.scene.selectedItems()
        return items[0] if items else None

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
            QMessageBox.information(self, "Texte", "Sélectionne d'abord une forme.")
            return
        text, ok = QInputDialog.getText(self, "Texte de la forme", "Texte :", text=item.label)
        if ok:
            item.label = text
            item.update()

    def exportJsonToFile(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exporter le diagramme en JSON", "", "JSON (*.json)")
        if not path:
            return
        text = self.scene.to_json()
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        QMessageBox.information(self, "Export", f"Diagramme exporté dans {path}")

    def importJsonFromFile(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importer un diagramme JSON", "", "JSON (*.json)")
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
