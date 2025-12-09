from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QFileDialog, QMessageBox, QStatusBar
)
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox

from app.app_context import AppContext
from domain.models.project import Project
from domain.services.project_service import ProjectService
from domain.services.deps_generator import DepsGenerator
from infrastructure.repositories.project_repository import ProjectRepository

from ui.pages.start_page import StartPage
from ui.pages.wizard.wizard_page import WizardPage


class MainWindow(QMainWindow):
    def __init__(self, context: AppContext, parent=None):
        super().__init__(parent)
        self.context = context
        self.project_service = ProjectService()
        self.project_repository = ProjectRepository()
        self.deps_generator = DepsGenerator()

        self.setWindowTitle("DEPS Designer")
        self.resize(1200, 800)

        # Pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_page = StartPage(on_new=self.new_project, on_open=self.open_project_dialog)
        self.wizard_page = WizardPage(app_context=self.context, on_project_changed=self.on_project_changed)
        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.wizard_page)
        self.stack.setCurrentWidget(self.start_page)

        # Menus + actions
        self._create_actions()
        self._create_menus()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()

    # ---------- Menus ----------

    def _create_actions(self):
        self.action_new = QAction("&Nouveau projet", self)
        self.action_new.triggered.connect(self.new_project)

        self.action_open = QAction("&Ouvrir…", self)
        self.action_open.triggered.connect(self.open_project_dialog)

        self.action_save = QAction("&Enregistrer", self)
        self.action_save.triggered.connect(self.save_project)

        self.action_save_as = QAction("Enregistrer &sous…", self)
        self.action_save_as.triggered.connect(self.save_project_as)

        self.action_export_deps = QAction("Exporter &DEPS…", self)
        self.action_export_deps.triggered.connect(self.export_deps)

        self.action_validate = QAction("&Valider le projet", self)
        self.action_validate.triggered.connect(self.validate_project)

        self.action_quit = QAction("&Quitter", self)
        self.action_quit.triggered.connect(self.close)

        # Édition (placeholder pour l’instant)
        self.action_undo = QAction("Annuler", self)
        self.action_redo = QAction("Rétablir", self)

        # Affichage (placeholder)
        self.action_reset_view = QAction("Réinitialiser la vue", self)
        # par ex: connecter à la vue courante plus tard

        # Aide
        self.action_about = QAction("À propos", self)
        self.action_about.triggered.connect(self.show_about)

    def _create_menus(self):
        menu_file = self.menuBar().addMenu("&Fichier")
        menu_file.addAction(self.action_new)
        menu_file.addAction(self.action_open)
        menu_file.addSeparator()
        menu_file.addAction(self.action_save)
        menu_file.addAction(self.action_save_as)
        menu_file.addSeparator()
        menu_file.addAction(self.action_export_deps)
        menu_file.addSeparator()
        menu_file.addAction(self.action_quit)

        menu_edit = self.menuBar().addMenu("&Édition")
        menu_edit.addAction(self.action_undo)
        menu_edit.addAction(self.action_redo)

        menu_view = self.menuBar().addMenu("&Affichage")
        menu_view.addAction(self.action_reset_view)

        menu_help = self.menuBar().addMenu("&Aide")
        menu_help.addAction(self.action_about)

    def show_about(self):
        QMessageBox.information(
            self,
            "À propos de DEPS Designer",
            "DEPS Designer\n\nOutil de conception de diagrammes logiques "
            "et de génération de code DEPS.",
        )
    # ---------- Actions ----------

    def new_project(self):
        project = Project.create(name="Nouveau projet")
        self.context.set_project(project, path=None)
        self.wizard_page.set_project(project)
        self.stack.setCurrentWidget(self.wizard_page)
        self.update_status_bar()

    def open_project_dialog(self):
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un projet",
            "",
            "Projet DEPS (*.depsproj);;Tous les fichiers (*.*)",
        )
        if not path_str:
            return
        path = Path(path_str)
        project = self.project_repository.load(path)
        self.context.set_project(project, path)
        self.wizard_page.set_project(project)
        self.stack.setCurrentWidget(self.wizard_page)
        self.update_status_bar()

    def save_project(self):
        if self.context.current_project is None:
            return
        if self.context.current_path is None:
            self.save_project_as()
            return
        self.project_repository.save(self.context.current_project, self.context.current_path)
        self.context.is_dirty = False
        self.update_status_bar()

    def save_project_as(self):
        if self.context.current_project is None:
            return
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le projet sous…",
            "",
            "Projet DEPS (*.depsproj)",
        )
        if not path_str:
            return
        path = Path(path_str)
        if path.suffix != ".depsproj":
            path = path.with_suffix(".depsproj")

        self.project_repository.save(self.context.current_project, path)
        self.context.set_project(self.context.current_project, path)
        self.update_status_bar()

    def export_deps(self):
        if self.context.current_project is None:
            return
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter le code DEPS…",
            "",
            "Fichier DEPS (*.deps);;Texte (*.txt)",
        )
        if not path_str:
            return
        path = Path(path_str)
        if path.suffix == "":
            path = path.with_suffix(".deps")

        code = self.deps_generator.generate(self.context.current_project)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code, encoding="utf-8")

        self.status_bar.showMessage(f"Code DEPS exporté vers {path}", 5000)

    def validate_project(self):
        if self.context.current_project is None:
            return
        issues = self.project_service.validate_project(self.context.current_project)
        if not issues:
            QMessageBox.information(self, "Validation", "Aucune erreur trouvée.")
        else:
            msg = "\n".join(
                f"- [{i.severity}] {i.message}" for i in issues[:20]
            )
            QMessageBox.warning(self, "Validation", msg)

    def on_project_changed(self):
        self.context.mark_dirty()
        self.update_status_bar()

    def update_status_bar(self):
        if self.context.current_project is None:
            self.status_bar.showMessage("Aucun projet chargé.")
            return

        path_text = str(self.context.current_path) if self.context.current_path else "(non enregistré)"
        dirty = "Modifié" if self.context.is_dirty else "Sauvegardé"
        self.status_bar.showMessage(
            f"Projet : {self.context.current_project.name} | {dirty} | Fichier : {path_text}"
        )
