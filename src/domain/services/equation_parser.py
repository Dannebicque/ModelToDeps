from typing import Tuple, List
from domain.models.equations import Expr, Var, Not, And, Or, EquationError


class EquationSyntaxError(Exception):
    def __init__(self, message: str, position: int | None = None):
        super().__init__(message)
        self.position = position


class EquationParser:
    """
    Parser très simple pour des équations du type :
    A & B | !C
    avec opérateurs : !, &, |, parenthèses.
    """

    def parse(self, text: str) -> Expr:
        # TODO: implémenter un parser réel (shunting-yard ou recursive descent)
        # Ici on met juste un stub pour la structure :
        text = text.strip()
        if not text:
            raise EquationSyntaxError("Équation vide", position=0)
        # Exemple minimal : expression = une variable unique
        return Var(name=text)

    def validate(self, text: str) -> List[EquationError]:
        try:
            self.parse(text)
            return []
        except EquationSyntaxError as e:
            return [EquationError(message=str(e), position=e.position)]
