from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Protocol, TypeVar

import lox.expr as e
from lox.tokens import Token

T = TypeVar("T", covariant=True)


@dataclass
class Stmt(abc.ABC):
    """Base class"""

    @abc.abstractmethod
    def accept(self, visitor: Visitor[T]) -> T:
        pass


class Visitor(Protocol[T]):
    def visit_expression(self, expr: Expression) -> T:
        pass

    def visit_print(self, expr: Print) -> T:
        pass

    def visit_var(self, expr: Var) -> T:
        pass

    def visit_block(self, expr: Block) -> T:
        pass


@dataclass
class Expression(Stmt):
    expression: e.Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_expression(self)


@dataclass
class Print(Stmt):
    expression: e.Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_print(self)


@dataclass
class Var(Stmt):
    name: Token
    initializer: e.Expr | None

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_var(self)


@dataclass
class Block(Stmt):
    statments: list[Stmt | None]

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_block(self)
