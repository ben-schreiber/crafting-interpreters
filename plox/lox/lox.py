import sys
from pathlib import Path

from lox.errors import handler
from lox.scanner import Scanner


def run(source: str) -> None:
    for token in Scanner(source):
        print(token)


def run_file(path: str) -> None:
    file = Path(path).read_text(encoding="utf-8")
    run(file)
    if handler.had_error:
        sys.exit(65)


def run_prompt() -> None:
    try:
        while True:
            run(input("> "))
            handler.had_error = False
    except KeyboardInterrupt:
        return


def main() -> None:
    if len(sys.args) > 1:
        print("Usage: plox [script]")
        sys.exit(64)
    if len(sys.args) == 1:
        run_file(sys.args[1])
    else:
        run_prompt()


if __name__ == "__main__":
    main()
