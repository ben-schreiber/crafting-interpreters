from typing import Any

from lox.errors import LoxRuntimeError
from lox.tokens import Token


class Environment:

    def __init__(self) -> None:
        self.__values: dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self.__values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.__values:
            return self.__values[name.lexeme]
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
