from __future__ import annotations

import time
from typing import Any

import lox.expr as e
import lox.stmt as s
from lox.environment import Environment
from lox.errors import LoxRuntimeError, ReturnError, handler
from lox.lox_callable import LoxCallable
from lox.lox_class import LoxClass, LoxInstance
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
        self.locals: dict[e.Expr, int] = {}
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

    def resolve(self, expr: e.Expr, depth: int) -> None:
        self.locals[expr] = depth

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

    def visit_expression(self, stmt: s.Expression) -> Any:
        self.__evaluate(stmt.expression)
        return None

    def visit_print(self, stmt: s.Print) -> Any:
        value = self.__evaluate(stmt.expression)
        print(self.__stringify(value))
        return None

    def visit_var(self, stmt: s.Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self.__evaluate(stmt.initializer)
        self.__environment.define(stmt.name.lexeme, value)

    def visit_variable(self, expr: e.Variable) -> Any:
        return self.__look_up_variable(expr.name, expr)

    def __look_up_variable(self, name: Token, expr: e.Expr) -> Any:
        distance = self.locals.get(expr)
        if distance is None:
            return self.globals.get(name)
        return self.__environment.get_at(distance, name.lexeme)

    def visit_assign(self, expr: e.Assign) -> Any:
        value = self.__evaluate(expr.value)

        distance = self.locals.get(expr)
        if distance is None:
            self.globals.assign(expr.name, value)
        else:
            self.__environment.assign_at(distance, expr.name, value)

        return value

    def visit_block(self, stmt: s.Block) -> Any:
        self.execute_block(stmt.statments, Environment(self.__environment))

    def execute_block(self, statements: list[s.Stmt | None], environment: Environment) -> None:
        previous = self.__environment
        try:
            self.__environment = environment
            for statement in statements:
                self.__execute(statement)
        finally:
            self.__environment = previous

    def visit_if(self, stmt: s.If) -> Any:
        if self.__is_truthy(self.__evaluate(stmt.condition)):
            self.__execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.__execute(stmt.else_branch)

    def visit_logical(self, expr: e.Logical) -> Any:
        left = self.__evaluate(expr.left)

        if expr.operator.type_ == TokenType.OR:
            if self.__is_truthy(left):
                return left
        elif not self.__is_truthy(left):
            return left

        return self.__evaluate(expr.right)

    def visit_while(self, stmt: s.While) -> Any:
        while self.__is_truthy(self.__evaluate(stmt.condition)):
            self.__execute(stmt.body)

    def visit_call(self, expr: e.Call) -> Any:
        callee: LoxCallable = self.__evaluate(expr.callee)
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
        arguments = [self.__evaluate(arg) for arg in expr.arguments]
        if len(arguments) != callee.arity:
            raise LoxRuntimeError(expr.paren, f"Expected {callee.arity} arguments but got {len(arguments)}.")
        return callee(self, arguments)

    def visit_function(self, stmt: s.Function) -> Any:
        function = LoxFunction(stmt, self.__environment, False)
        self.__environment.define(stmt.name.lexeme, function)

    def visit_return(self, stmt: s.Return) -> Any:
        value: Any = None
        if stmt.value is not None:
            value = self.__evaluate(stmt.value)

        raise ReturnError(value)

    def visit_class(self, stmt: s.Class) -> Any:
        self.__environment.define(stmt.name.lexeme, None)
        methods = {
            method.name.lexeme: LoxFunction(method, self.__environment, method.name.lexeme == "init")
            for method in stmt.methods
        }
        klass = LoxClass(stmt.name.lexeme, methods)
        self.__environment.assign(stmt.name, klass)

    def visit_get(self, expr: e.Get) -> Any:
        obj = self.__evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise LoxRuntimeError(expr.name, "Only instances have properties.")

    def visit_set(self, expr: e.Set) -> Any:
        obj = self.__evaluate(expr.obj)
        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")

        value = self.__evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_this(self, expr: e.This) -> Any:
        return self.__look_up_variable(expr.keyword, expr)
