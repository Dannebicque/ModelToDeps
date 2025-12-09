# ui/pages/wizard/step_status.py
from enum import Enum


class StepStatus(Enum):
    INCOMPLETE = "incomplete"   # gris
    VALID = "valid"             # vert
    INVALID = "invalid"         # rouge
