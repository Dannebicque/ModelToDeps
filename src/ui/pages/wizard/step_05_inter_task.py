# ui/pages/wizard/step_03_task.py

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QSplitter,
)
from PySide6.QtCore import Qt

from domain.models.project import StepData
from domain.models.diagram import Diagram, DiagramType, Node, NodeType
from ui.widgets.diagram_view import DiagramView
from ui.widgets.component_library import ComponentLibraryWidget
from .base_step import BaseWizardStep
from .step_status import StepStatus


class Step05InterTask(BaseWizardStep):
    """
    Étape 3 : logique.
    Palette de composants logiques + zone de dessin.
    """

    def __init__(self, step_id: str, on_changed, parent=None):
        super().__init__(step_id=step_id, on_changed=on_changed, parent=parent)

        self._diagram: Diagram | None = None

        # Palette de composants (exemple)
        self.component_library = ComponentLibraryWidget(
            title="Composants logiques",
            components=["Contact NO", "Contact NF", "Bobine", "Temporisation"],
            on_component_selected=self._on_component_selected,
        )

        # Zone de dessin
        self.diagram_view = DiagramView(on_changed=self._on_diagram_changed)

        # Toolbar zoom/focus
        toolbar = QHBoxLayout()
        btn_zoom_in = QPushButton("Zoom +")
        btn_zoom_out = QPushButton("Zoom -")
        btn_reset = QPushButton("Réinitialiser vue")

        btn_zoom_in.clicked.connect(self.diagram_view.zoom_in)
        btn_zoom_out.clicked.connect(self.diagram_view.zoom_out)
        btn_reset.clicked.connect(self.diagram_view.reset_view)

        toolbar.addWidget(btn_zoom_in)
        toolbar.addWidget(btn_zoom_out)
        toolbar.addWidget(btn_reset)
        toolbar.addStretch()

        # Splitter : gauche palette, droite diagramme
        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(self.component_library)
        splitter.addWidget(self.diagram_view)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout()
        layout.addLayout(toolbar)
        layout.addWidget(splitter)
        self.setLayout(layout)

    # -- Chargement des données métier --

    def load_from_step(self, step: StepData) -> None:
        super().load_from_step(step)

        if not step.diagrams:
            from domain.models.diagram import Diagram
            step.diagrams.append(
                Diagram(
                    id="logic_main",
                    name="Logique principale",
                    diagram_type=DiagramType.LOGIC,
                )
            )
        self._diagram = step.diagrams[0]
        self.diagram_view.set_diagram(self._diagram)

    # -- Palette -> diagramme --

    def _on_component_selected(self, name: str):
        if not self._diagram:
            return

        # Exemple simple : on ajoute un node au centre
        node = Node.create(
            node_type=NodeType.CONDITION,
            label=name,
            x=50,
            y=50,
        )
        self._diagram.nodes.append(node)
        self.diagram_view.add_node(node)
        self.mark_changed()

    def _on_diagram_changed(self):
        # appelé par DiagramView quand un node bouge etc.
        self.mark_changed()

    # -- Statut de l'étape --

    def get_status(self) -> StepStatus:
        """
        Pour l'instant : si au moins un node, on dit VALID,
        sinon INCOMPLETE.
        Plus tard, tu remplacerais ça par une vraie validation métier.
        """
        if self._diagram and self._diagram.nodes:
            return StepStatus.VALID
        return StepStatus.INCOMPLETE
