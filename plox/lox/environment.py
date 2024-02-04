from __future__ import annotations

from typing import Any

from lox.errors import LoxRuntimeError
from lox.tokens import Token


class Environment:
    def __init__(self, enclosing: Environment | None = None) -> None:
        self.__values: dict[str, Any] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: Any) -> None:
        self.__values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.__values:
            return self.__values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.__values:
            self.__values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
