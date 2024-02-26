from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Protocol, TypeVar

import lox.expr as e
from lox.tokens import Token

T = TypeVar("T", covariant=True)


@dataclass(frozen=True)
class Stmt(abc.ABC):
    """Base class"""

    @abc.abstractmethod
    def accept(self, visitor: Visitor[T]) -> T:
        pass


class Visitor(Protocol[T]):
    def visit_expression(self, stmt: Expression) -> T:
        pass

    def visit_print(self, stmt: Print) -> T:
        pass

    def visit_var(self, stmt: Var) -> T:
        pass

    def visit_block(self, stmt: Block) -> T:
        pass

    def visit_if(self, stmt: If) -> T:
        pass

    def visit_while(self, stmt: While) -> T:
        pass

    def visit_function(self, stmt: Function) -> T:
        pass

    def visit_return(self, stmt: Return) -> T:
        pass

    def visit_class(self, stmt: Class) -> T:
        pass


@dataclass(frozen=True)
class Expression(Stmt):
    expression: e.Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_expression(self)


@dataclass(frozen=True)
class Print(Stmt):
    expression: e.Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_print(self)


@dataclass(frozen=True)
class Var(Stmt):
    name: Token
    initializer: e.Expr | None

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_var(self)


@dataclass(frozen=True)
class Block(Stmt):
    statments: list[Stmt | None]

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_block(self)


@dataclass(frozen=True)
class If(Stmt):
    condition: e.Expr
    then_branch: Stmt
    else_branch: Stmt | None

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_if(self)


@dataclass(frozen=True)
class While(Stmt):
    condition: e.Expr
    body: Stmt

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_while(self)


@dataclass(frozen=True)
class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_function(self)


@dataclass(frozen=True)
class Return(Stmt):
    keyword: Token
    value: e.Expr | None

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_return(self)


@dataclass(frozen=True)
class Class(Stmt):
    name: Token
    methods: list[Function]

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_class(self)
