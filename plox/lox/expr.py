from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from lox.tokens import Token

T = TypeVar("T", covariant=True)


@dataclass(frozen=True)
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

    def visit_assign(self, expr: Assign) -> T:
        pass

    def visit_logical(self, expr: Logical) -> T:
        pass

    def visit_call(self, expr: Call) -> T:
        pass


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_binary(self)


@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_grouping(self)


@dataclass(frozen=True)
class Literal(Expr):
    value: Any

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_literal(self)


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_unary(self)


@dataclass(frozen=True)
class Variable(Expr):
    name: Token

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_variable(self)


@dataclass(frozen=True)
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_assign(self)


@dataclass(frozen=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_logical(self)


@dataclass(frozen=True)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_call(self)
