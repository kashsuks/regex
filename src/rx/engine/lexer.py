from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    LITERAL = auto()
    DOT = auto()
    STAR = auto()
    PLUS = auto()
    QUESTION = auto()
    PIPE = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    CARET = auto()
    DOLLAR = auto()
    ANCHOR_START = auto()  # ^ at the start of the pattern
    ESCAPE = auto()
    CHAR_CLASS = auto()
    QUANTIFIER = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    position: int

    def __repr__(self) -> str:
        return f"Token{self.type.name}, {self.value!r}, pos={self.position}"


class LexerError(Exception):
    def __init__(self, message: str, position: int):
        super().__init__(message)
        self.position = position


class Lexer:
    """
    Tokenizes a regex pattern string into a list of Token objects

    Supports: literals, . * + ? | () [] ^ $ \\ escapes
    """

    ESCAPE_SEQUENCES = {"d", "D", "w", "W", "s", "S", "n", "t", "r"}

    def __init__(self, pattern: str):
        self._pattern = pattern
        self._pos = 0
        self._tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        self._tokens = []
        self._pos = 0

        while self._pos < len(self._pattern):
            self._read_next()

        self._tokens.append(Token(TokenType.EOF, "", self._pos))
        return self._tokens

    # below are all the private helpers for this Lexer

    def _current(self) -> str:
        return self._pattern[self._pos]

    def _advance(self) -> str:
        ch = self._pattern[self._pos]
        self._pos += 1
        return ch

    def _read_next(self) -> None:
        pos = self._pos
        ch = self._advance()

        simple_map = {
            ".": TokenType.DOT,
            "*": TokenType.STAR,
            "+": TokenType.PLUS,
            "?": TokenType.QUESTION,
            "|": TokenType.PIPE,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "$": TokenType.DOLLAR,
        }

        if ch == "{":
            self._read_brace_quantifier(pos)
        elif ch == "\\":
            self._read_escape(pos)
        elif ch == "[":
            self._read_char_class(pos)
        elif ch == "^":
            # anchor only at position 0
            if pos == 0:
                self._tokens.append(Token(TokenType.ANCHOR_START, "^", pos))
            else:
                self._tokens.append(Token(TokenType.CARET, "^", pos))
        elif ch in simple_map:
            self._tokens.append(Token(simple_map[ch], ch, pos))
        else:
            self._tokens.append(Token(TokenType.LITERAL, ch, pos))

    def _read_escape(self, start: int) -> None:
        if self._pos >= len(self._pattern):
            raise LexerError("Trailing backlash in pattern", start)
        ch = self._advance()
        if ch not in self.ESCAPE_SEQUENCES and not ch.isprintable():
            raise LexerError(f"Unknown escape sequence: \\{ch}", start)
        self._tokens.append(Token(TokenType.ESCAPE, f"\\{ch}", start))

    def _read_char_class(self, start: int) -> None:
        """
        Reads [...] as a single CHAR_CLASS token
        """

        content = "["
        if self._pos < len(self._pattern) and self._current() == "^":
            content += self._advance()  # include the negation ^

        # allow ] as first char inside class
        if self._pos < len(self._pattern) and self._current() == "]":
            content += self._advance()

        while self._pos < len(self._pattern):
            ch = self._advance()
            content += ch

            if ch == "]":
                self._tokens.append(Token(TokenType.CHAR_CLASS, content, start))
                return
            if ch == "\\" and self._pos < len(self._pattern):
                content += self._advance()  # include the escaped char

        raise LexerError("Unterminated character class", start)

    def _read_brace_quantifier(self, start: int) -> None:
        """ "
        Attempt to read {n}, {n,} or {n, m} as a QUANTIFIER token

        If the content does not match the expected format, fall back
        to emitting as a literal
        """

        saved_pos = self._pos
        content = "{"

        while self._pos < len(self._pattern) and self._current() != "}":
            content += self._advance()

        if self._pos >= len(self._pattern):
            self._pos = saved_pos
            self._tokens.append(Token(TokenType.LITERAL, "{", start))
            return

        content += self._advance()  # consume the closing }
        inner = content[1:-1]

        import re as _re

        if not _re.fullmatch(r"\d+(,\d*)?", inner):
            self._pos = saved_pos
            self._tokens.append(Token(TokenType.LITERAL, "{", start))
            return

        self._tokens.append(Token(TokenType.QUANTIFIER, content, start))
