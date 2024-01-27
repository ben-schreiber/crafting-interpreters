from typing import Any

import lox.expr as e
import lox.stmt as s
from lox.environment import Environment
from lox.errors import LoxRuntimeError, handler
from lox.expr import Variable
from lox.stmt import Var
from lox.token_type import TokenType
from lox.tokens import Token


class Interpreter(e.Visitor[Any], s.Visitor[Any]):

    def __init__(self) -> None:
        self.__environment = Environment()

    def visit_literal(self, expr: e.Literal) -> Any:
        return expr.value

    def visit_grouping(self, expr: e.Grouping) -> Any:
        return self.__evaluate(expr.expression)

    def __evaluate(self, expr: e.Expr) -> Any:
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

    def interpret(self, statements: list[s.Stmt]) -> None:
        try:
            for stmt in statements:
                self.__execute(stmt)
        except LoxRuntimeError as e:
            handler.runtime_error(e)

    def __execute(self, stmt: s.Stmt) -> None:
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
