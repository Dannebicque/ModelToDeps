# ui/pages/wizard/wizard_page.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, List, Dict

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
)
from PySide6.QtCore import Qt

from app.app_context import AppContext
from domain.models.project import Project

from .base_step import BaseWizardStep
from .step_status import StepStatus

from .step_01_archi import Step01Archi
from .step_02_signaux import Step02Signaux
from .step_03_logic import Step03Logic
# ... à compléter avec tes autres steps


@dataclass
class StepMeta:
    id: str
    title: str
    widget: BaseWizardStep


class WizardPage(QWidget):
    def __init__(self, app_context: AppContext, on_project_changed: Callable[[], None], parent=None):
        super().__init__(parent)
        self.app_context = app_context
        self.on_project_changed = on_project_changed

        self.current_project: Optional[Project] = None

        self.stack = QStackedWidget()
        self.step_buttons: List[QPushButton] = []
        self.steps: List[StepMeta] = []
        self.step_status: Dict[str, StepStatus] = {}

        self._build_steps()
        self._build_ui()
        self.update_step_statuses()

    # -----------------------------------------------------
    # Construction
    # -----------------------------------------------------

    def _build_steps(self):
        def make_step(widget_cls, step_id: str, title: str) -> StepMeta:
            widget = widget_cls(step_id=step_id, on_changed=self._on_step_changed)
            return StepMeta(id=step_id, title=title, widget=widget)

        self.steps = [
            make_step(Step01Archi, "step_01_archi", "Architecture"),
            make_step(Step02Signaux, "step_02_signaux", "Signaux / IO"),
            make_step(Step03Logic, "step_03_logic", "Logique"),
            # ajoute ici les autres :
            # make_step(Step04Safety, "step_04_safety", "Sécurité"),
            # make_step(Step05Sequences, "step_05_sequences", "Séquences"),
            # make_step(Step06Summary, "step_06_summary", "Synthèse"),
        ]

        for meta in self.steps:
            self.stack.addWidget(meta.widget)
            self.step_status[meta.id] = StepStatus.INCOMPLETE

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # --- Barre d'étapes en haut ---
        steps_bar = QHBoxLayout()
        steps_bar.setSpacing(4)

        for idx, meta in enumerate(self.steps):
            btn = QPushButton(f"{idx + 1}. {meta.title}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx: self._on_step_button_clicked(i))
            self.step_buttons.append(btn)
            steps_bar.addWidget(btn)

        steps_bar.addStretch()

        layout.addLayout(steps_bar)
        layout.addWidget(self.stack)

        self.setLayout(layout)

        # On démarre à l'étape 0
        self.set_current_step(0, force=True)

    # -----------------------------------------------------
    # Navigation
    # -----------------------------------------------------

    def set_project(self, project: Project):
        self.current_project = project

        # Propager les données vers chaque step
        for meta in self.steps:
            step_data = project.steps.get(meta.id)
            if step_data:
                meta.widget.load_from_step(step_data)

        self.set_current_step(0, force=True)
        self.update_step_statuses()

    def set_current_step(self, index: int, force: bool = False):
        if index < 0 or index >= len(self.steps):
            return

        if not force and not self._is_step_enabled(index):
            return

        self.stack.setCurrentIndex(index)
        self._update_step_buttons_checked(index)

    def _update_step_buttons_checked(self, current_index: int):
        for idx, btn in enumerate(self.step_buttons):
            btn.setChecked(idx == current_index)

    def _on_step_button_clicked(self, index: int):
        if self._is_step_enabled(index):
            self.set_current_step(index)

    def _is_step_enabled(self, index: int) -> bool:
        """
        Règle de verrouillage :
        - Étape 0 toujours accessible
        - Étape n accessible seulement si toutes les étapes < n sont VALID
        """
        if index == 0:
            return True

        for prev_idx in range(0, index):
            meta = self.steps[prev_idx]
            if self.step_status.get(meta.id) != StepStatus.VALID:
                return False
        return True

    # -----------------------------------------------------
    # Statuts des étapes
    # -----------------------------------------------------

    def update_step_statuses(self):
        """
        Recalcule les statuts à partir des widgets d'étapes,
        puis met à jour les couleurs des boutons.
        """
        for meta in self.steps:
            status = meta.widget.get_status()
            self.step_status[meta.id] = status

        self._refresh_step_buttons_style()

    def _refresh_step_buttons_style(self):
        status_colors = {
            StepStatus.INCOMPLETE: "#b2bec3",  # gris
            StepStatus.VALID: "#00b894",       # vert
            StepStatus.INVALID: "#d63031",     # rouge
        }

        for idx, meta in enumerate(self.steps):
            btn = self.step_buttons[idx]
            status = self.step_status.get(meta.id, StepStatus.INCOMPLETE)
            color = status_colors[status]

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 4px;
                    padding: 6px 10px;
                    color: white;
                    font-weight: 500;
                }}
                QPushButton:checked {{
                    border: 2px solid #2d3436;
                }}
            """)

            # Gérer l'état enabled/disabled
            enabled = self._is_step_enabled(idx)
            btn.setEnabled(enabled)

    # -----------------------------------------------------
    # Modifications
    # -----------------------------------------------------

    def _on_step_changed(self):
        """
        Appelé par les steps quand l'utilisateur modifie quelque chose.
        """
        self.update_step_statuses()
        self.on_project_changed()
