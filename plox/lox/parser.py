import lox.expr as e
import lox.stmt as s
from lox.errors import handler
from lox.token_type import TokenType
from lox.tokens import Token


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._current = 0

    def parse(self) -> list[s.Stmt | None]:
        statements: list[s.Stmt | None] = []
        while not self.__is_at_end:
            statements.append(self.__declaration())
        return statements

    def __declaration(self) -> s.Stmt | None:
        try:
            if self.__match(TokenType.VAR):
                return self.__var_declaration()
            return self.__statement()
        except ParseError:
            self.__synchronize()
            return None

    def __var_declaration(self) -> s.Stmt:
        name = self.__consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.__match(TokenType.EQUAL):
            initializer = self.__expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return s.Var(name, initializer)

    def __statement(self) -> s.Stmt:
        if self.__match(TokenType.FOR):
            return self.__for_statement()
        if self.__match(TokenType.IF):
            return self.__if_statement()
        if self.__match(TokenType.PRINT):
            return self.__print_statement()
        if self.__match(TokenType.WHILE):
            return self.__while_statement()
        if self.__match(TokenType.LEFT_BRACE):
            return s.Block(self.__block())
        return self.__expression_statement()

    def __for_statement(self) -> s.Stmt:
        self.__consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.__match(TokenType.SEMICOLON):
            initializer: s.Stmt | None = None
        elif self.__match(TokenType.VAR):
            initializer = self.__var_declaration()
        else:
            initializer = self.__expression_statement()

        condition: e.Expr | None = None
        if not self.__check(TokenType.SEMICOLON):
            condition = self.__expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: e.Expr | None = None
        if not self.__check(TokenType.RIGHT_PAREN):
            increment = self.__expression()
        self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.__statement()

        if increment is not None:
            body = s.Block([body, s.Expression(increment)])

        if condition is None:
            condition = e.Literal(True)

        body = s.While(condition, body)
        if initializer is not None:
            body = s.Block([initializer, body])

        return body

    def __while_statement(self) -> s.Stmt:
        self.__consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.__expression()
        self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.__statement()
        return s.While(condition, body)

    def __if_statement(self) -> s.Stmt:
        self.__consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.__expression()
        self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.__statement()
        else_branch: s.Stmt | None = None
        if self.__match(TokenType.ELSE):
            else_branch = self.__statement()
        return s.If(condition, then_branch, else_branch)

    def __block(self) -> list[s.Stmt | None]:
        statments: list[s.Stmt | None] = []
        while not self.__check(TokenType.RIGHT_BRACE) and not self.__is_at_end:
            statments.append(self.__declaration())
        self.__consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statments

    def __expression_statement(self) -> s.Stmt:
        expr = self.__expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return s.Expression(expr)

    def __print_statement(self) -> s.Stmt:
        value = self.__expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return s.Print(value)

    def __expression(self) -> e.Expr:
        return self.__assignment()

    def __assignment(self) -> e.Expr:
        expr = self.__or()

        if self.__match(TokenType.EQUAL):
            equals = self.__previous
            value = self.__assignment()

            if isinstance(expr, e.Variable):
                name = expr.name
                return e.Assign(name, value)

            self.__error(equals, "Invalid assignment target.")

        return expr

    def __or(self) -> e.Expr:
        expr = self.__and()

        while self.__match(TokenType.OR):
            operator = self.__previous
            right = self.__and()
            expr = e.Logical(expr, operator, right)

        return expr

    def __and(self) -> e.Expr:
        expr = self.__equality()

        while self.__match(TokenType.AND):
            operator = self.__previous
            right = self.__equality()
            expr = e.Logical(expr, operator, right)

        return expr

    def __equality(self) -> e.Expr:
        expr = self.__comparison()

        while self.__match(TokenType.BANG, TokenType.BANG_EQUAL):
            operator = self.__previous
            right = self.__comparison()
            expr = e.Binary(expr, operator, right)

        return expr

    def __match(self, *types: TokenType) -> bool:
        for type_ in types:
            if self.__check(type_):
                self.__advance()
                return True

        return False

    def __check(self, type_: TokenType) -> bool:
        if self.__is_at_end:
            return False

        return self.__peek().type_ == type_

    def __advance(self) -> Token:
        if not self.__is_at_end:
            self._current += 1

        return self.__previous

    @property
    def __is_at_end(self) -> bool:
        return self.__peek().type_ == TokenType.EOF

    def __peek(self) -> Token:
        return self._tokens[self._current]

    @property
    def __previous(self) -> Token:
        return self._tokens[self._current - 1]

    def __comparison(self) -> e.Expr:
        expr = self.__term()

        while self.__match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.__previous
            right = self.__term()
            expr = e.Binary(expr, operator, right)

        return expr

    def __term(self) -> e.Expr:
        expr = self.__factor()

        while self.__match(TokenType.MINUS, TokenType.PLUS):
            operator = self.__previous
            right = self.__factor()
            expr = e.Binary(expr, operator, right)

        return expr

    def __factor(self) -> e.Expr:
        expr = self.__unary()

        while self.__match(TokenType.SLASH, TokenType.STAR):
            operator = self.__previous
            right = self.__unary()
            expr = e.Binary(expr, operator, right)

        return expr

    def __unary(self) -> e.Expr:
        if self.__match(TokenType.BANG, TokenType.MINUS):
            operator = self.__previous
            right = self.__unary()
            return e.Unary(operator, right)

        return self.__primary()

    def __primary(self) -> e.Expr:
        if self.__match(TokenType.FALSE):
            return e.Literal(False)
        if self.__match(TokenType.TRUE):
            return e.Literal(True)
        if self.__match(TokenType.NIL):
            return e.Literal(None)
        if self.__match(TokenType.NUMBER, TokenType.STRING):
            return e.Literal(self.__previous.literal)
        if self.__match(TokenType.IDENTIFIER):
            return e.Variable(self.__previous)
        if self.__match(TokenType.LEFT_PAREN):
            expr = self.__expression()
            self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return e.Grouping(expr)

        raise self.__error(self.__peek(), "Expect expression.")

    def __consume(self, type_: TokenType, message: str) -> Token:
        if self.__check(type_):
            return self.__advance()

        raise self.__error(self.__peek(), message)

    def __error(self, token: Token, message: str) -> ParseError:
        handler.error_token(token, message)
        return ParseError()

    def __synchronize(self) -> None:
        self.__advance()

        while not self.__is_at_end:
            if self.__previous.type_ == TokenType.SEMICOLON:
                return

            match self.__peek().type_:
                case (
                    TokenType.CLASS
                    | TokenType.FUN
                    | TokenType.VAR
                    | TokenType.FOR
                    | TokenType.IF
                    | TokenType.WHILE
                    | TokenType.PRINT
                    | TokenType.RETURN
                ):
                    return

            self.__advance()
