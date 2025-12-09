from typing import List
from domain.models.project import Project
from domain.models.validation import ValidationIssue, Severity
from domain.services.equation_parser import EquationParser


class ProjectService:
    def __init__(self):
        self._parser = EquationParser()

    def validate_project(self, project: Project) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        # Exemples de règles :
        # - nom de projet non vide
        if not project.name.strip():
            issues.append(ValidationIssue(
                severity=Severity.ERROR,
                message="Le nom du projet est vide."
            ))

        # - vérification des équations sur tous les noeuds de type CONDITION
        for step_id, step in project.steps.items():
            for diagram in step.diagrams:
                for node in diagram.nodes:
                    eq = node.properties.get("equation")
                    if eq:
                        for err in self._parser.validate(eq):
                            issues.append(ValidationIssue(
                                severity=Severity.ERROR,
                                message=f"[{node.label}] {err.message}",
                                step_id=step_id,
                                diagram_id=diagram.id,
                                node_id=node.id,
                                equation_position=err.position,
                            ))

        return issues
