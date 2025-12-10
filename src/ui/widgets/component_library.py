# ui/widgets/component_library.py

from typing import Callable, List, Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
)
from PySide6.QtGui import QPainter, QBrush, QPen, QColor
from PySide6.QtCore import Qt, QSize

from domain.models.diagram import DiagramComponent, NodeShape, BorderStyle


class ComponentPreview(QWidget):
    def __init__(self, component: DiagramComponent, parent=None):
        super().__init__(parent)
        self.component = component
        self.setMinimumHeight(48)

    def sizeHint(self) -> QSize:  # noqa: D401
        return QSize(120, 48)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(8, 8, -8, -8)
        appearance = self.component.appearance

        pen = QPen(QColor(appearance.border_color))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(appearance.fill_color)))

        if appearance.shape == NodeShape.ELLIPSE:
            painter.drawEllipse(rect)
            if appearance.border == BorderStyle.DOUBLE:
                painter.drawEllipse(rect.adjusted(5, 5, -5, -5))
        else:
            painter.drawRoundedRect(rect, 6, 6)
            if appearance.border == BorderStyle.DOUBLE:
                painter.drawRoundedRect(rect.adjusted(5, 5, -5, -5), 6, 6)

        painter.drawText(rect, Qt.AlignCenter, self.component.display_name)


class ComponentLibraryWidget(QWidget):
    """Palette graphique réutilisable."""

    def __init__(
        self,
        title: str,
        components: Optional[List[DiagramComponent]] = None,
        on_component_selected: Optional[Callable[[DiagramComponent], None]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._on_component_selected = on_component_selected
        self._components: List[DiagramComponent] = components or []

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

    def set_components(self, components: List[DiagramComponent]):
        self._components = components
        self.list_widget.clear()
        for comp in components:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, comp)
            widget = ComponentPreview(comp)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        if self._on_component_selected:
            comp: DiagramComponent = item.data(Qt.UserRole)
            self._on_component_selected(comp)
