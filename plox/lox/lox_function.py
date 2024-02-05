from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lox.environment import Environment
from lox.errors import ReturnError
from lox.lox_callable import LoxCallable

if TYPE_CHECKING:
    from lox.interpreter import Interpreter
    from lox.stmt import Function


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment) -> None:
        self.__declaration = declaration
        self.arity = len(self.__declaration.params)
        self.__closure = closure

    def __call__(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        environment = Environment(self.__closure)

        for param, argument in zip(self.__declaration.params, arguments):
            environment.define(param.lexeme, argument)

        try:
            interpreter.execute_block(self.__declaration.body, environment)
        except ReturnError as return_value:
            return return_value.value

    def __str__(self) -> str:
        return f"<fn {self.__declaration.name.lexeme}>"
