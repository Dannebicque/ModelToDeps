# ui/widgets/component_library.py

from typing import Callable, List, Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
)
from PySide6.QtGui import QPainter, QBrush, QPen, QColor, QDrag
from PySide6.QtCore import Qt, QSize, QMimeData
from PySide6.QtWidgets import QListWidget
from domain.models.diagram import DiagramComponent, NodeShape, BorderStyle


class ComponentPreview(QWidget):
    def __init__(self, component: DiagramComponent, parent=None):
        super().__init__(parent)
        self.component = component
        self.setMinimumHeight(64)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)

    def sizeHint(self) -> QSize:  # noqa: D401
        return QSize(140, 64)

    def paintEvent(self, event):
        comp = self.component
        if comp is None or not hasattr(comp, "appearance"):
            return

        appearance = comp.appearance
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing, True)

            rect = self.rect().adjusted(10, 10, -10, -10)

            pen = QPen(QColor(appearance.border_color))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(appearance.fill_color)))

            if appearance.shape == NodeShape.ELLIPSE:
                painter.drawEllipse(rect)
                if appearance.border == BorderStyle.DOUBLE:
                    painter.drawEllipse(rect.adjusted(6, 6, -6, -6))
            else:
                painter.drawRoundedRect(rect, 8, 8)
                if appearance.border == BorderStyle.DOUBLE:
                    painter.drawRoundedRect(rect.adjusted(6, 6, -6, -6), 8, 8)

            painter.setPen(QPen(QColor(appearance.text_color)))
            painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, comp.display_name)
        finally:
            if painter.isActive():
                painter.end()


class ComponentLibraryItemWidget(QWidget):
    """Composite widget: display name + preview box."""

    def __init__(self, component: DiagramComponent, parent=None):
        super().__init__(parent)
        self.component = component

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        name_label = QLabel(component.display_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-weight: 600; font-size: 12px;")

        preview = ComponentPreview(component)

        for widget in (self, name_label, preview):
            widget.setToolTip(component.display_name)

        layout.addWidget(name_label)
        layout.addWidget(preview)

        self.setLayout(layout)


class DraggableComponentList(QListWidget):
    MIME_TYPE = "application/x-diagram-component"

    def __init__(
        self,
        on_component_selected: Optional[Callable[[DiagramComponent], None]] = None,
        on_component_activated: Optional[Callable[[DiagramComponent], None]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._on_component_selected = on_component_selected
        self._on_component_activated = on_component_activated
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setDragEnabled(True)
        self.currentItemChanged.connect(self._handle_selection_change)
        self.itemDoubleClicked.connect(self._handle_double_click)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
        component: DiagramComponent = item.data(Qt.UserRole)
        if component is None or not hasattr(component, "id"):
            return
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setData(self.MIME_TYPE, component.id.encode())
        drag.setMimeData(mime_data)
        drag.exec(Qt.CopyAction)

    def _handle_selection_change(self, current: QListWidgetItem, previous: QListWidgetItem):  # noqa: ARG002
        if self._on_component_selected and current:
            component: DiagramComponent = current.data(Qt.UserRole)
            if component:
                self._on_component_selected(component)

    def _handle_double_click(self, item: QListWidgetItem):
        if self._on_component_activated and item:
            component: DiagramComponent = item.data(Qt.UserRole)
            if component:
                self._on_component_activated(component)


class ComponentLibraryWidget(QWidget):
    """Palette graphique réutilisable."""

    def __init__(
        self,
        title: str,
        components: Optional[List[DiagramComponent]] = None,
        on_component_selected: Optional[Callable[[DiagramComponent], None]] = None,
        on_component_activated: Optional[Callable[[DiagramComponent], None]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._on_component_selected = on_component_selected
        self._on_component_activated = on_component_activated
        self._components: List[DiagramComponent] = components or []

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        self.list_widget = DraggableComponentList(
            on_component_selected=self._on_component_selected,
            on_component_activated=self._on_component_activated,
        )
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

        self.set_components(self._components)

    def set_components(self, components: List[DiagramComponent]):
        self._components = components
        self.list_widget.clear()
        for comp in components:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, comp)

            if hasattr(comp, "display_name"):
                item.setToolTip(getattr(comp, "display_name"))
                widget = ComponentLibraryItemWidget(comp)
                item.setSizeHint(widget.sizeHint())
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, widget)
            else:
                item.setText(str(comp))
                item.setToolTip(str(comp))
                self.list_widget.addItem(item)
