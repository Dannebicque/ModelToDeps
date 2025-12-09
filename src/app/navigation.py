from PySide6.QtWidgets import QMainWindow, QStackedWidget
from ui.pages.home_page import HomePage
from ui.pages.wizard_page import WizardPage
from ui.pages.editor_page import EditorPage

class NavigationController(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = HomePage(on_open_project=self.open_project,
                                  on_new_project=self.new_project)
        self.wizard_page = WizardPage(on_finished=self.on_wizard_finished)
        self.editor_page = EditorPage()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.wizard_page)
        self.stack.addWidget(self.editor_page)

        self.stack.setCurrentWidget(self.home_page)

    def open_project(self, project_path: str):
        # chargement via repository, puis passage à la vue d’édition
        from infrastructure.repositories.project_repository import ProjectRepository
        repo = ProjectRepository()
        project = repo.load(project_path)
        self.editor_page.set_project(project)
        self.stack.setCurrentWidget(self.editor_page)

    def new_project(self):
        self.stack.setCurrentWidget(self.wizard_page)

    def on_wizard_finished(self, project):
        # project = instance de domain.models.project.Project
        self.editor_page.set_project(project)
        self.stack.setCurrentWidget(self.editor_page)
