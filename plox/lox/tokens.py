from dataclasses import dataclass
from typing import Any

from lox.token_type import TokenType


@dataclass
class Token:
    type_: TokenType
    lexeme: str
    literal: Any
    line: int

    def __str__(self) -> str:
        return f"{self.type_} {self.lexeme} {self.literal}"
