from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from domain.models.project import Project
from ui.widgets.diagram_view import DiagramView
from ui.widgets.property_panel import PropertyPanel

class EditorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._project: Project | None = None

        self.diagram_view = DiagramView()
        self.property_panel = PropertyPanel()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Éditeur de projet"))
        layout.addWidget(self.diagram_view)
        layout.addWidget(self.property_panel)
        self.setLayout(layout)

    def set_project(self, project: Project):
        self._project = project
        # Mettre à jour la vue avec le diagramme courant
        if project.diagrams:
            self.diagram_view.load_diagram(project.diagrams[0])
