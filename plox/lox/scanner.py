from typing import Any, Generator

from lox.errors import handler
from lox.token import Token
from lox.token_type import TokenType


class Scanner:
    def __init__(self, source: str) -> None:
        self.source = source
        self.current = self.start = 0
        self.line = 1
        self.tokens = []

    @property
    def at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self) -> Token | None:
        match self.advance():
            case "(" | ")" | "{" | "}" | "," | "." | "-" | "+" | ";" | "*" as token:
                return self.add_token(TokenType(token))
            case "!":
                return self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
            case "=":
                return self.add_token(TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL)
            case "<":
                return self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
            case ">":
                return self.add_token(TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER)
            case "/":
                if self.match("/"):
                    while self.peek != "\n" and not self.at_end:
                        self.advance()
                else:
                    return self.add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case '"':
                return self.string()
            case "o":
                if self.match("r"):
                    return self.add_token(TokenType.OR)
            case _ as c:
                if c.isdigit():
                    return self.number()
                elif c.isalpha():
                    return self.identifier()
                else:
                    handler.error(self.line, "Unexpected character")

    def identifier(self) -> Token:
        while self.peek.isalnum():
            self.advance()
        return self.add_token(TokenType.IDENTIFIER)

    def number(self) -> Token:
        while self._is_digit(self.peek):
            self.advance()
        if self.peek == "." and self._is_digit(self.peek_next):
            self.advance()
            while self._is_digit(self.peek):
                self.advance()
        return self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    @property
    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def string(self) -> Token:
        while (peek := self.peek) != '"' and not self.at_end:
            if peek == "\n":
                self.line += 1
            self.advance()

        if not self.at_end:
            handler.error(self.line, "Unterminated string.")
            return

        self.advance()
        return self.add_token(TokenType.STRING, self.source[self.start + 1 : self.current - 1])

    def match(self, expected: str) -> bool:
        if self.at_end or self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    @property
    def peek(self) -> str:
        if self.at_end:
            return "\0"
        return self.source[self.current]

    def __iter__(self) -> Generator[Token, None, None]:
        while not self.at_end:
            self.start = self.current
            if token := self.scan_token():
                yield token

        yield Token(TokenType.EOF, "", None, self.line)

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def add_token(self, type_: TokenType, literal: Any | None = None) -> Token:
        text = self.source[self.start : self.current]
        return Token(type_, text, literal, self.line)
