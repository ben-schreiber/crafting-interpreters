from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lox.errors import LoxRuntimeError
from lox.lox_callable import LoxCallable

if TYPE_CHECKING:
    from lox.interpreter import Interpreter
    from lox.lox_function import LoxFunction
    from lox.tokens import Token


class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: dict[str, LoxFunction]) -> None:
        self.name = name
        self.__methods = methods

    def __str__(self) -> str:
        return self.name

    def __call__(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        instance = LoxInstance(self)
        if initializer := self.find_method("init"):
            initializer.bind(instance)(interpreter, arguments)
        return instance

    @property
    def arity(self) -> int:
        if initializer := self.find_method("init"):
            return initializer.arity
        return 0

    def find_method(self, name: str) -> LoxFunction:
        return self.__methods.get(name)


class LoxInstance:
    def __init__(self, klass: LoxClass) -> None:
        self.__klass = klass
        self.__fields: dict[str, Any] = {}

    def get(self, name: Token) -> Any:
        if name.lexeme in self.__fields:
            return self.__fields[name.lexeme]

        if method := self.__klass.find_method(name.lexeme):
            return method.bind(self)

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any) -> None:
        self.__fields[name.lexeme] = value

    def __str__(self) -> str:
        return f"{self.__klass.name} instance"
