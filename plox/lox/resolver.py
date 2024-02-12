from contextlib import contextmanager
from enum import Enum

import lox.expr as e
import lox.stmt as s
from lox.errors import handler
from lox.interpreter import Interpreter
from lox.tokens import Token


class FunctionType(Enum):
    NONE = "none"
    FUNCTION = "function"


class Resolver(e.Visitor[None], s.Visitor[None]):
    def __init__(self, interpreter: Interpreter) -> None:
        self.__interpreter = interpreter
        self.__scopes: list[dict[str, bool]] = []
        self.__current_function: FunctionType = FunctionType.NONE

    @contextmanager
    def use_scope(self) -> None:
        try:
            self.__scopes.append({})
            yield
        finally:
            self.__scopes.pop()

    @contextmanager
    def function(self, type_: FunctionType) -> None:
        try:
            enclosing_function = self.__current_function
            self.__current_function = type_
            yield
        finally:
            self.__current_function = enclosing_function

    def resolve(self, stmt: list[s.Stmt | e.Expr] | s.Stmt | e.Expr) -> None:
        if not isinstance(stmt, list):
            stmt = [stmt]
        for s in stmt:
            s.accept(self)

    def visit_block(self, stmt: s.Block) -> None:
        with self.use_scope():
            self.resolve(stmt.statments)

    def visit_var(self, stmt: s.Var) -> None:
        self.__declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.__define(stmt.name)

    def __declare(self, name: Token) -> None:
        if len(self.__scopes) > 0:
            if name.lexeme in self.__scopes[-1]:
                handler.error_token(name, "Already a variable with this name in this scope.")
            self.__scopes[-1][name.lexeme] = False

    def __define(self, name: Token) -> None:
        if len(self.__scopes) > 0:
            self.__scopes[-1][name.lexeme] = True

    def visit_variable(self, expr: e.Variable) -> None:
        if len(self.__scopes) == 0 and not self.__scopes[-1][expr.name.lexeme]:
            handler.error_token(expr.name, "Can't read local variable in its own initializer.")

        self.__resolve_local(expr, expr.name)

    def __resolve_local(self, expr: e.Expr, name: Token) -> None:
        for idx, scope in enumerate(reversed(self.__scopes)):
            if name.lexeme in scope:
                self.__interpreter.resolve(expr, idx)

    def visit_assign(self, expr: e.Assign) -> None:
        self.resolve(expr.value)
        self.__resolve_local(expr, expr.name)

    def visit_function(self, stmt: s.Function) -> None:
        self.__declare(stmt.name)
        self.__define(stmt.name)

        self.__resolve_function(stmt, FunctionType.FUNCTION)

    def __resolve_function(self, function: s.Stmt, type_: FunctionType) -> None:
        with self.function(type_), self.use_scope():
            for param in function.params:
                self.__declare(param)
                self.__define(param)

            self.resolve(function.body)

    def visit_expression(self, stmt: s.Expression) -> None:
        self.resolve(stmt.expression)

    def visit_if(self, stmt: s.If) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)

    def visit_print(self, stmt: s.Print) -> None:
        self.resolve(stmt.expression)

    def visit_return(self, stmt: s.Return) -> None:
        if self.__current_function == FunctionType.NONE:
            handler.error_token(stmt.keyword, "Can't return from top-level code.")
        if stmt.value is not None:
            self.resolve(stmt.value)

    def visit_while(self, stmt: s.While) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_binary(self, expr: e.Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call(self, expr: e.Call) -> None:
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)

    def visit_grouping(self, expr: e.Grouping) -> None:
        self.resolve(expr.expression)

    def visit_literal(self, expr: e.Literal) -> None:
        pass

    def visit_logical(self, expr: e.Logical) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_unary(self, expr: e.Unary) -> None:
        self.resolve(expr.right)
