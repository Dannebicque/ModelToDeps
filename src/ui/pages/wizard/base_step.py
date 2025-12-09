# ui/pages/wizard/base_step.py

from typing import Optional, Callable
from PySide6.QtWidgets import QWidget
from domain.models.project import StepData
from .step_status import StepStatus


class BaseWizardStep(QWidget):
    def __init__(self, step_id: str, on_changed: Callable[[], None], parent=None):
        super().__init__(parent)
        self.step_id = step_id
        self._on_changed = on_changed
        self._step_data: Optional[StepData] = None

    def load_from_step(self, step: StepData) -> None:
        """
        Chargement des données métier pour cette étape.
        À surcharger si besoin dans les sous-classes (mais appeler super()).
        """
        self._step_data = step

    def get_status(self) -> StepStatus:
        """
        Renvoie l'état de l'étape :
        - pour l'instant : INCOMPLETE partout
        - plus tard : tu pourras ici lancer tes validations.
        """
        return StepStatus.INCOMPLETE

    def mark_changed(self) -> None:
        """
        À appeler quand l'utilisateur modifie quelque chose.
        Notifie le wizard (MainWindow sera prévenu via le callback).
        """
        self._on_changed()
