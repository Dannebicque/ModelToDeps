# ui/pages/start_page.py

from typing import Callable, Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtCore import Qt


class StartPage(QWidget):
    """
    Page d'accueil de l'application : propose de créer un nouveau projet
    ou d'en ouvrir un existant.

    Les callbacks on_new et on_open sont fournis par MainWindow.
    """

    def __init__(
        self,
        on_new: Callable[[], None],
        on_open: Callable[[], None],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self._on_new = on_new
        self._on_open = on_open

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Titre
        title = QLabel("DEPS Designer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
            }
        """)

        # Sous-titre / description
        subtitle = QLabel(
            "Outil de conception de diagrammes logiques et de génération de code DEPS.\n"
            "Commencez par créer un nouveau projet ou en ouvrir un existant."
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
            }
        """)

        # Espace avant les boutons
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacerItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Bouton "Nouveau projet"
        btn_new = QPushButton("Nouveau projet")
        btn_new.setMinimumWidth(220)
        btn_new.setMinimumHeight(40)
        btn_new.clicked.connect(self._on_new)
        btn_new.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
            }
        """)

        # Bouton "Ouvrir un projet"
        btn_open = QPushButton("Ouvrir un projet…")
        btn_open.setMinimumWidth(220)
        btn_open.setMinimumHeight(40)
        btn_open.clicked.connect(self._on_open)
        btn_open.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px 16px;
            }
        """)

        # Organisation verticale
        layout.addWidget(btn_new, alignment=Qt.AlignHCenter)
        layout.addWidget(btn_open, alignment=Qt.AlignHCenter)

        # Espace bas pour centrer le bloc
        layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)
