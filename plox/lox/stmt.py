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

    def visit_if(self, expr: If) -> T:
        pass

    def visit_while(self, expr: While) -> T:
        pass

    def visit_function(self, expr: Function) -> T:
        pass

    def visit_return(self, expr: Return) -> T:
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


@dataclass
class If(Stmt):
    condition: e.Expr
    then_branch: Stmt
    else_branch: Stmt | None

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_if(self)


@dataclass
class While(Stmt):
    condition: e.Expr
    body: Stmt

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_while(self)


@dataclass
class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_function(self)


@dataclass
class Return(Stmt):
    keyword: Token
    value: e.Expr | None

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_return(self)
