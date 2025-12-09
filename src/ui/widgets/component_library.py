# ui/widgets/component_library.py

from typing import Callable, List, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PySide6.QtCore import Qt


class ComponentLibraryWidget(QWidget):
    """
    Palette simple : liste de composants cliquables.
    Le callback on_component_selected reçoit le nom du composant.
    """

    def __init__(
        self,
        title: str,
        components: Optional[List[str]] = None,
        on_component_selected: Optional[Callable[[str], None]] = None,
        parent=None
    ):
        super().__init__(parent)
        self._on_component_selected = on_component_selected
        self._components = components or []

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        label = QLabel(title)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

        self.set_components(self._components)

    def set_components(self, components: List[str]):
        self._components = components
        self.list_widget.clear()
        for name in components:
            QListWidgetItem(name, self.list_widget)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        if self._on_component_selected:
            self._on_component_selected(item.text())
