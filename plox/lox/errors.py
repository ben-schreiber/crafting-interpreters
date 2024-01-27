from lox.token_type import TokenType
from lox.tokens import Token


class LoxRuntimeError(Exception):
    def __init__(self, token: Token, message: str, *args: object) -> None:
        super().__init__(message, *args)
        self.token = token
        self.message = message


class ErrorHandler:
    def __init__(self) -> None:
        self.had_error = False
        self.had_runtime_error = False

    def error(self, line: int, message: str) -> None:
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}")
        self.had_error = True

    def error_token(self, token: Token, message: str) -> None:
        if token.type_ == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)

    def runtime_error(self, error: LoxRuntimeError) -> None:
        print(f"{error.message}\n[line {error.token.line}]")
        self.had_runtime_error = True


handler = ErrorHandler()
