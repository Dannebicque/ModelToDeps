from pathlib import Path
from typing import Optional
from domain.models.project import Project


class AppContext:
    def __init__(self):
        self.current_project: Optional[Project] = None
        self.current_path: Optional[Path] = None
        self.is_dirty: bool = False

    def set_project(self, project: Project, path: Optional[Path] = None):
        self.current_project = project
        self.current_path = path
        self.is_dirty = False

    def mark_dirty(self):
        self.is_dirty = True
