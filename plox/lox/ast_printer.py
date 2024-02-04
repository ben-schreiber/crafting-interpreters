from lox.expr import Binary, Expr, Grouping, Literal, Unary, Visitor
from lox.token_type import TokenType
from lox.tokens import Token


class AstPrinter(Visitor[str]):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visit_binary(self, expr: Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping(self, expr: Grouping) -> str:
        return self._parenthesize("group", expr.expression)

    def visit_literal(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary(self, expr: Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        return f"({name} {' '.join(expr.accept(self) for expr in exprs)})"


if __name__ == "__main__":
    e = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )
    print(AstPrinter().print(e))
