from dataclasses import dataclass
from typing import List


@dataclass
class Expr:
    pass


@dataclass
class Var(Expr):
    name: str


@dataclass
class Not(Expr):
    expr: Expr


@dataclass
class And(Expr):
    left: Expr
    right: Expr


@dataclass
class Or(Expr):
    left: Expr
    right: Expr


@dataclass
class EquationError:
    message: str
    position: int | None = None
