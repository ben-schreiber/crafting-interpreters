from dataclasses import dataclass

from lox.token import Token


@dataclass
class Expr:
    """Base class"""


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr