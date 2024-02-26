from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from lox.environment import Environment
from lox.errors import ReturnError
from lox.lox_callable import LoxCallable

if TYPE_CHECKING:
    from lox.interpreter import Interpreter
    from lox.lox_class import LoxInstance
    from lox.stmt import Function


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool) -> None:
        self.__declaration = declaration
        self.arity = len(self.__declaration.params)
        self.__closure = closure
        self.__is_initializer = is_initializer

    def __call__(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        environment = Environment(self.__closure)

        for param, argument in zip(self.__declaration.params, arguments):
            environment.define(param.lexeme, argument)

        try:
            interpreter.execute_block(self.__declaration.body, environment)
        except ReturnError as return_value:
            if self.__is_initializer:
                return self.__closure.get_at(0, "this")
            return return_value.value

        if self.__is_initializer:
            return self.__closure.get_at(0, "this")

    def __str__(self) -> str:
        return f"<fn {self.__declaration.name.lexeme}>"

    def bind(self, instance: LoxInstance) -> Self:
        environment = Environment(self.__closure)
        environment.define("this", instance)
        return LoxFunction(self.__declaration, environment, self.__is_initializer)
