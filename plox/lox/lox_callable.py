from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from lox.interpreter import Interpreter


@runtime_checkable
class LoxCallable(Protocol):
    arity: int

    def __call__(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        pass
