# ui/pages/wizard/step_03_task.py

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QSplitter,
    QComboBox,
    QLabel,
)
from PySide6.QtCore import Qt, QPointF

from domain.models.project import StepData
from domain.models.diagram import (
    Diagram,
    DiagramType,
    Node,
    Connection,
    DiagramComponent,
    ConnectionType,
)
from domain.models.component_catalog import default_components
from ui.widgets.diagram_view import DiagramView
from ui.widgets.component_library import ComponentLibraryWidget
from .base_step import BaseWizardStep
from .step_status import StepStatus


class Step01System(BaseWizardStep):
    """
    Étape 3 : logique.
    Palette de composants logiques + zone de dessin.
    """

    def __init__(self, step_id: str, on_changed, parent=None):
        super().__init__(step_id=step_id, on_changed=on_changed, parent=parent)

        self._diagram: Diagram | None = None
        self._components = default_components()
        self._components_by_id = {c.id: c for c in self._components}
        self._active_component: DiagramComponent | None = None

        # Palette de composants (exemple)
        self.component_library = ComponentLibraryWidget(
            title="Bibliothèque graphique",
            components=self._components,
            on_component_selected=self._on_component_focused,
            on_component_activated=self._on_component_activated,
        )

        # Zone de dessin
        self.diagram_view = DiagramView(on_changed=self._on_diagram_changed)
        self.diagram_view.set_component_adder(self._on_component_dropped)

        # Toolbar zoom/focus
        toolbar = QHBoxLayout()
        btn_zoom_in = QPushButton("Zoom +")
        btn_zoom_out = QPushButton("Zoom -")
        btn_reset = QPushButton("Réinitialiser vue")
        btn_connect = QPushButton("Relier la sélection")
        self.connection_type_combo = QComboBox()
        self.connection_type_combo.addItem("Standard", ConnectionType.DEFAULT)
        self.connection_type_combo.addItem("Flux", ConnectionType.FLOW)
        self.connection_type_combo.addItem("Condition", ConnectionType.CONDITION)
        self.connection_type_combo.addItem("Boucle", ConnectionType.FEEDBACK)

        btn_zoom_in.clicked.connect(self.diagram_view.zoom_in)
        btn_zoom_out.clicked.connect(self.diagram_view.zoom_out)
        btn_reset.clicked.connect(self.diagram_view.reset_view)
        btn_connect.clicked.connect(self._connect_selected)

        toolbar.addWidget(btn_zoom_in)
        toolbar.addWidget(btn_zoom_out)
        toolbar.addWidget(btn_reset)
        toolbar.addWidget(btn_connect)
        toolbar.addWidget(self.connection_type_combo)
        toolbar.addStretch()

        helper = QLabel(
            "Sélectionnez un composant, puis glissez-le dans la zone ou cliquez sur un espace vide pour l'ajouter."
        )
        helper.setWordWrap(True)

        # Splitter : gauche palette, droite diagramme
        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(self.component_library)
        splitter.addWidget(self.diagram_view)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout()
        layout.addLayout(toolbar)
        layout.addWidget(helper)
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

    def _on_component_focused(self, component: DiagramComponent):
        self._active_component = component
        self.diagram_view.set_active_component(component.id)

    def _on_component_activated(self, component: DiagramComponent):
        center_scene = self.diagram_view.mapToScene(
            self.diagram_view.viewport().rect().center()
        )
        self._create_node(component, center_scene)

    def _on_component_dropped(self, component_id: str, position: QPointF):
        component = self._components_by_id.get(component_id)
        if component:
            self._create_node(component, position)

    def _create_node(self, component: DiagramComponent, position: QPointF | None = None):
        if not self._diagram:
            return

        pos_x = position.x() if position else 50
        pos_y = position.y() if position else 50

        node = Node.create(
            node_type=component.node_type,
            label=component.display_name,
            x=pos_x,
            y=pos_y,
            appearance=component.appearance,
            properties=component.default_properties.copy(),
        )
        self._diagram.nodes.append(node)
        self.diagram_view.add_node(node)
        self.mark_changed()

    def _connect_selected(self):
        if not self._diagram:
            return
        selected = list(self.diagram_view.get_selected_node_ids())
        if len(selected) < 2:
            return
        connection_type: ConnectionType = self.connection_type_combo.currentData()
        connection = Connection.create(
            selected[0],
            selected[1],
            connection_type=connection_type or ConnectionType.DEFAULT,
        )
        self._diagram.connections.append(connection)
        self.diagram_view.add_connection(connection)
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
