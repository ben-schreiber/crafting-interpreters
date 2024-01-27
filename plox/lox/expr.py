from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from lox.tokens import Token

T = TypeVar("T", covariant=True)


@dataclass
class Expr(abc.ABC):
    """Base class"""

    @abc.abstractmethod
    def accept(self, visitor: Visitor[T]) -> T:
        pass


class Visitor(Protocol[T]):
    def visit_binary(self, expr: Binary) -> T:
        pass

    def visit_grouping(self, expr: Grouping) -> T:
        pass

    def visit_literal(self, expr: Literal) -> T:
        pass

    def visit_unary(self, expr: Unary) -> T:
        pass

    def visit_variable(self, expr: Variable) -> T:
        pass


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_binary(self)


@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_grouping(self)


@dataclass
class Literal(Expr):
    value: Any

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_literal(self)


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_unary(self)


@dataclass
class Variable(Expr):
    name: Token

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_variable(self)
