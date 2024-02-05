from __future__ import annotations

import time
from typing import Any

import lox.expr as e
import lox.stmt as s
from lox.environment import Environment
from lox.errors import LoxRuntimeError, ReturnError, handler
from lox.lox_callable import LoxCallable
from lox.lox_function import LoxFunction
from lox.token_type import TokenType
from lox.tokens import Token


class _ClockCallable(LoxCallable):
    def __init__(self) -> None:
        self.arity = 0

    def __call__(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        return time.time()

    def __str__(self) -> str:
        return "<native fn>"


class Interpreter(e.Visitor[Any], s.Visitor[Any]):
    def __init__(self) -> None:
        self.globals = Environment()
        self.__environment = self.globals

        self.globals.define("clock", _ClockCallable())

    def visit_literal(self, expr: e.Literal) -> Any:
        return expr.value

    def visit_grouping(self, expr: e.Grouping) -> Any:
        return self.__evaluate(expr.expression)

    def __evaluate(self, expr: e.Expr | None) -> Any:
        if expr is None:
            return
        return expr.accept(self)

    def visit_unary(self, expr: e.Unary) -> Any:
        right = self.__evaluate(expr.right)

        match expr.operator.type_:
            case TokenType.BANG:
                return not self.__is_truthy(right)
            case TokenType.MINUS:
                self.__check_number_operand(expr.operator, right)
                return -float(right)

        return None

    @staticmethod
    def __check_number_operand(operator: Token, operand: Any) -> None:
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")

    def __is_truthy(self, object: Any) -> bool:
        if object is None:
            return False

        if isinstance(object, bool):
            return bool(object)

        return True

    def visit_binary(self, expr: e.Binary) -> Any:
        left = self.__evaluate(expr.left)
        right = self.__evaluate(expr.right)

        match expr.operator.type_:
            case TokenType.GREATER:
                self.__check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.__check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self.__check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.__check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TokenType.BANG_EQUAL:
                return not self.__is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.__is_equal(left, right)
            case TokenType.MINUS:
                self.__check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.SLASH:
                self.__check_number_operands(expr.operator, left, right)
                return float(left) / float(right)
            case TokenType.STAR:
                self.__check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")

        return None

    @staticmethod
    def __check_number_operands(operator: Token, left: Any, right: Any) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")

    def __is_equal(self, a: Any, b: Any) -> bool:
        if a is None and b is None:
            return True

        return bool(a == b)

    def interpret(self, statements: list[s.Stmt | None]) -> None:
        try:
            for stmt in statements:
                self.__execute(stmt)
        except LoxRuntimeError as e:
            handler.runtime_error(e)

    def __execute(self, stmt: s.Stmt | None) -> None:
        if stmt is None:
            return
        stmt.accept(self)

    @staticmethod
    def __stringify(__o: Any) -> str:
        if __o is None:
            return "nil"
        if isinstance(__o, float):
            text = str(__o)
            if text.endswith(".0"):
                text = text.replace(".0", "")
            return text

        return str(__o)

    def visit_expression(self, expr: s.Expression) -> Any:
        self.__evaluate(expr.expression)
        return None

    def visit_print(self, expr: s.Print) -> Any:
        value = self.__evaluate(expr.expression)
        print(self.__stringify(value))
        return None

    def visit_var(self, stmt: s.Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self.__evaluate(stmt.initializer)
        self.__environment.define(stmt.name.lexeme, value)

    def visit_variable(self, expr: e.Variable) -> Any:
        return self.__environment.get(expr.name)

    def visit_assign(self, expr: e.Assign) -> Any:
        value = self.__evaluate(expr.value)
        self.__environment.assign(expr.name, value)
        return value

    def visit_block(self, expr: s.Block) -> Any:
        self.execute_block(expr.statments, Environment(self.__environment))

    def execute_block(self, statements: list[s.Stmt | None], environment: Environment) -> None:
        previous = self.__environment
        try:
            self.__environment = environment
            for statement in statements:
                self.__execute(statement)
        finally:
            self.__environment = previous

    def visit_if(self, expr: s.If) -> Any:
        if self.__is_truthy(self.__evaluate(expr.condition)):
            self.__execute(expr.then_branch)
        elif expr.else_branch is not None:
            self.__execute(expr.else_branch)

    def visit_logical(self, expr: e.Logical) -> Any:
        left = self.__evaluate(expr.left)

        if expr.operator.type_ == TokenType.OR:
            if self.__is_truthy(left):
                return left
        elif not self.__is_truthy(left):
            return left

        return self.__evaluate(expr.right)

    def visit_while(self, expr: s.While) -> Any:
        while self.__is_truthy(self.__evaluate(expr.condition)):
            self.__execute(expr.body)

    def visit_call(self, expr: e.Call) -> Any:
        callee: LoxCallable = self.__evaluate(expr.callee)
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
        arguments = [self.__evaluate(arg) for arg in expr.arguments]
        if len(arguments) != callee.arity:
            raise LoxRuntimeError(expr.paren, f"Expected {callee.arity} arguments but got {len(arguments)}.")
        return callee(self, arguments)

    def visit_function(self, expr: s.Function) -> Any:
        function = LoxFunction(expr, self.__environment)
        self.__environment.define(expr.name.lexeme, function)

    def visit_return(self, expr: s.Return) -> Any:
        value: Any = None
        if expr.value is not None:
            value = self.__evaluate(expr.value)

        raise ReturnError(value)
