import sys
from pathlib import Path

from lox.ast_printer import AstPrinter
from lox.errors import handler
from lox.interpreter import Interpreter
from lox.parser import Parser
from lox.scanner import Scanner


def run(source: str, interpreter: Interpreter) -> None:
    tokens = list(Scanner(source))
    parser = Parser(tokens)
    statements = parser.parse()

    if handler.had_error or statements is None:
        return

    interpreter.interpret(statements)


def run_file(path: str) -> None:
    file = Path(path).read_text(encoding="utf-8")
    run(file, Interpreter())
    if handler.had_error:
        sys.exit(65)
    if handler.had_runtime_error:
        sys.exit(70)


def run_prompt() -> None:
    i = Interpreter()
    try:
        while True:
            run(input("> "), i)
            handler.had_error = False
    except KeyboardInterrupt:
        return


def main() -> None:
    if len(sys.argv) == 1:
        return run_prompt()

    if len(sys.argv) == 2:
        return run_file(sys.argv[1])

    print("Usage: plox [script]")
    sys.exit(64)


if __name__ == "__main__":
    main()
