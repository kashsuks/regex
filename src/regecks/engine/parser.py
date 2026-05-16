from __future__ import annotations

from typing import Optional

from .lexer import Lexer, Token, TokenType
from .models import (
    AlternationNode,
    AnchorEndNode,
    AnchorStartNode,
    ASTNode,
    CharClassNode,
    ConcatNode,
    DotNode,
    EscapeNode,
    GroupNode,
    LiteralNode,
    CaseFoldNode,
    LookaheadNode,
    LookbehindNode,
    NamedGroupNode,
    NonCapturingGroupNode,
    QuantifierNode,
)


class ParseError(Exception):
    def __init__(self, message: str, position: int = -1):
        super().__init__(message)
        self.position = position


class Parser:
    """
    Recursive parser for regular expressions

    Grammar (simplified):
        expr        ::= alternation
        alternation ::= concat ("|" concat)*
        concat      ::= quantified*
        quantified* ::= atom quantifier?
        quantifier  ::= "*" | "+" | "?"
        atom        ::= LITERAL | DOT | ESCAPE | CHAR_CLASS
                        ANCHOR_START | DOLLAR | "(" expr ")"
    """

    def __init__(self, pattern: str) -> None:
        lexer = Lexer(pattern)
        self._tokens = lexer.tokenize()
        self._pos = 0
        self._group_counter = 0

    def parse(self) -> ASTNode:
        node = self._parse_alternation()
        self._expect(TokenType.EOF)
        return node

    # grammar rules below

    def _parse_alternation(self) -> ASTNode:
        branches: list[ASTNode] = [self._parse_concat()]
        while self._peek().type == TokenType.PIPE:
            self._advance()
            branches.append(self._parse_concat())
        if len(branches) == 1:
            return branches[0]
        return AlternationNode(alternatives=branches)

    def _parse_concat(self) -> ASTNode:
        children: list[ASTNode] = []
        while self._peek().type not in (
            TokenType.EOF,
            TokenType.PIPE,
            TokenType.RPAREN,
        ):
            children.append(self._parse_quantified())
        if len(children) == 1:
            return children[0]
        return ConcatNode(children=children)

    def _parse_quantified(self) -> ASTNode:
        atom = self._parse_atom()
        tok = self._peek()

        if tok.type == TokenType.STAR:
            self._advance()
            return QuantifierNode(child=atom, min=0, max=None)
        if tok.type == TokenType.PLUS:
            self._advance()
            return QuantifierNode(child=atom, min=1, max=None)
        if tok.type == TokenType.QUESTION:
            self._advance()
            return QuantifierNode(child=atom, min=0, max=1)
        if tok.type == TokenType.QUANTIFIER:
            self._advance()
            return self._parse_brace_quantifier(tok, atom)
        return atom

    def _parse_atom(self) -> ASTNode:
        tok = self._peek()

        if tok.type == TokenType.LITERAL:
            self._advance()
            return LiteralNode(char=tok.value)

        if tok.type == TokenType.DOT:
            self._advance()
            return DotNode()

        if tok.type == TokenType.ANCHOR_START:
            self._advance()
            return AnchorStartNode()

        if tok.type == TokenType.DOLLAR:
            self._advance()
            return AnchorEndNode()

        if tok.type == TokenType.ESCAPE:
            self._advance()
            return EscapeNode(sequence=tok.value)

        if tok.type == TokenType.CHAR_CLASS:
            self._advance()
            return self._parse_char_class_token(tok)

        if tok.type == TokenType.LPAREN:
            self._advance()
            return self._parse_group()

        raise ParseError(
            f"Unexpected token {tok.type.name} ({tok.value!r}) at position {tok.position}",
            tok.position,
        )

    def _parse_group(self) -> ASTNode:
        """
        Handles (, (?:, and (?P<name> and group prefixes

        Called after the opening ( has already been consumed.
        """
        
        if (
            self._peek().type == TokenType.QUESTION
            and self._pos + 1 < len(self._tokens)
        ):
            next_tok = self._tokens[self._pos + 1]

            if next_tok.type == TokenType.LITERAL and next_tok.value == "i":
                self._advance() # consume ?
                self._advance() # consume i
                self._expect(TokenType.RPAREN)

                rest = self._parse_alternation()
                return CaseFoldNode(child=rest)

            if next_tok.type == TokenType.LITERAL and next_tok.value == ":":
                self._advance() # consume ?
                self._advance() # consume :
                inner = self._parse_alternation()
                self._expect(TokenType.RPAREN)
                return NonCapturingGroupNode(child=inner)

            if next_tok.type == TokenType.LITERAL and next_tok.value == "P":
                self._advance() # consime ?
                self._advance() # consume P
                name = self._parse_group_name()
                self._group_counter += 1
                idx = self._group_counter
                inner = self._parse_alternation()
                self._expect(TokenType.RPAREN)
                return NamedGroupNode(child=inner, name=name, group_index=idx)

        self._group_counter += 1
        idx = self._group_counter
        inner = self._parse_alternation()
        self._expect(TokenType.RPAREN)
        return GroupNode(child=inner, group_index=idx)

    def _parse_group_name(self) -> str:
        """
        Parses <name> after (?P - consumes <, the name chars, and >
        """
        tok = self._advance()
        if tok.type != TokenType.LITERAL or tok.value != "<":
            raise ParseError(
                f"Expected '<' after (?P but got {tok.value!r}",
                tok.position,
            )

        name_chars = []
        while self._peek().type != TokenType.EOF:
            tok = self._peek()
            if tok.type == TokenType.LITERAL and tok.value == ">":
                self._advance() # consume >
                break
            if tok.type != TokenType.LITERAL:
                raise ParseError(
                    f"Invalid character in group name: {tok.value!r}",
                    tok.position,
                )
            name_chars.append(self._advance().value)

        if not name_chars:
            raise ParseError("Group name cannot be empty", -1)
        
        return "".join(name_chars)

    def _prase_group_name(self) -> str:
        """
        Parses <name> after (?P - consumes <, the name chars, and >
        """
        tok = self._advance()
        if tok.type != TokenType.LITERAL or tok.value != "<":
            raise ParseError(
                f"Expected '<' after (?P but got {tok.value!r}",
                tok.position,
            )

        name_chars = []
        while self._peek().type() != TokenType.EOF:
            tok = self._peek()
            if tok.type == TokenType.LITERAL and tok.value == ">":
                self._advance() # consume >
                break
            if tok.type not in (TokenType.LITERAL,):
                raise ParseError(
                    f"Invalid character in group name: {tok.value!r}",
                    tok.position,
                )
            name_chars.append(self._advance().value)

        if not name_chars:
            raise ParseError("Group name cannot be empty", -1)

        return "".join(name_chars)

    def _parse_char_class_token(self, tok: Token) -> CharClassNode:
        """
        Parses the values of a CHAR_CLASS token like "[a-z]" or "[^0-9]"
        """
        raw = tok.value
        inner = raw[1:-1]  # strip []
        negated = inner.startswith("^")
        if negated:
            inner = inner[1:]

        return CharClassNode(members=inner, negated=negated)

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        if tok.type != TokenType.EOF:
            self._pos += 1
        return tok

    def _expect(self, ttype: TokenType) -> Token:
        tok = self._advance()
        if tok.type != ttype:
            raise ParseError(
                f"Expected {ttype.name} but got {tok.type.name} at position {tok.position}",
                tok.position,
            )
        return tok

    def _parse_brace_quantifier(self, tok: Token, atom: ASTNode) -> QuantifierNode:
        """
        Parse a QUANTIFIER token value like {3}, {2,}, {1,4} into min/max
        """

        inner = tok.value[1:-1]

        if "," not in inner:
            n = int(inner)
            return QuantifierNode(child=atom, min=n, max=n)

        left, right = inner.split(",", 1)
        min_val = int(left)
        max_val = int(right) if right else None  # {n,} means unbounded

        if max_val is not None and max_val < min_val:
            raise ParseError(
                f"Invalid quantifier {{{inner}}}: max ({max_val}) < min({min_val})",
                tok.position,
            )

        return QuantifierNode(child=atom, min=min_val, max=max_val)
