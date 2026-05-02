from __future__ import annotations

from typing import Optional

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
    MatchResult,
    QuantifierNode,
)
from .parser import Parser


class Matcher:
    """
    Recursive backtracking Matcher

    Usage:
        matcher = Matcher("a+b")
        result = matcher.match("aab")
        results = matcher.find_all("aab ab")
    """

    def __init__(self, pattern: str) -> None:
        self._pattern = pattern
        parser = Parser(pattern)
        self._ast = parser.parse()
        self._groups: dict[int, tuple[int, int]] = {}

    def match(self, text: str) -> MatchResult:
        for start in range(len(text) + 1):
            self._groups = {}
            end = self._match_node(self._ast, text, start)
            if end is not None:
                groups = self._collect_groups(text)
                return MatchResult(
                    matched=True,
                    start=start,
                    end=end,
                    span=text[start:end],
                    groups=groups,
                )
        return MatchResult(matched=False, start=-1, end=-1, span="")

    def find_all(self, text: str) -> list[MatchResult]:
        """
        Return all non-overlapping matches
        """
        results: list[MatchResult] = []
        pos = 0
        while pos <= len(text):
            self._groups = {}
            end = self._match_node(self._ast, text, pos)
            if end is not None:
                groups = self._collect_groups(text)
                results.append(
                    MatchResult(
                        matched=True,
                        start=pos,
                        end=end,
                        span=text[pos:end],
                        groups=groups,
                    )
                )
                pos = end if end > pos else pos + 1
            else:
                pos += 1
        return results

    def _match_node(self, node: ASTNode, text: str, pos: int) -> Optional[int]:
        """
        Try to match node against text starting at pos

        Returns the new position on success, None on failure
        """
        if isinstance(node, LiteralNode):
            return self._match_literal(node, text, pos)

        if isinstance(node, DotNode):
            return self._match_dot(text, pos)

        if isinstance(node, AnchorStartNode):
            return pos if pos == 0 else None

        if isinstance(node, AnchorEndNode):
            return pos if pos == len(text) else None

        if isinstance(node, EscapeNode):
            return self._match_escape(node, text, pos)

        if isinstance(node, CharClassNode):
            return self._match_char_class(node, text, pos)

        if isinstance(node, ConcatNode):
            return self._match_concat(node, text, pos)

        if isinstance(node, AlternationNode):
            return self._match_alternation(node, text, pos)

        if isinstance(node, QuantifierNode):
            return self._match_quantifier(node, text, pos)

        if isinstance(node, GroupNode):
            return self._match_group(node, text, pos)

        raise RuntimeError(f"Unknown AST node type: {type(node)}")

    # node specific matchers

    def _match_literal(self, node: LiteralNode, text: str, pos: int) -> Optional[int]:
        if pos < len(text) and text[pos] == node.char:
            return pos + 1
        return None

    def _match_dot(self, text: str, pos: int) -> Optional[int]:
        if pos < len(text) and text[pos] != "\n":
            return pos + 1
        return None

    def _match_escape(self, node: EscapeNode, text: str, pos: int) -> Optional[int]:
        if pos >= len(text):
            return None
        ch = text[pos]
        seq = node.sequence  # eg "\\d"
        code = seq[1]

        matched = False
        if code == "d":
            matched = ch.isdigit()
        elif code == "D":
            matched = not ch.isdigit()
        elif code == "w":
            matched = ch.isalnum() or ch == "_"
        elif code == "W":
            matched = not (ch.isalnum() or ch == "_")
        elif code == "s":
            matched = ch in " \t\n\r\f\v"
        elif code == "S":
            matched = ch not in " \t\n\r\f\v"
        elif code == "n":
            matched = ch == "\n"
        elif code == "t":
            matched = ch == "\t"
        elif code == "r":
            matched = ch == "\r"
        else:
            # escaped literal
            matched = ch == code

        return pos + 1 if matched else None

    def _match_char_class(
        self, node: CharClassNode, text: str, pos: int
    ) -> Optional[int]:
        if pos >= len(text):
            return None
        ch = text[pos]
        in_class = self._char_in_class(ch, node.members)
        if node.negated:
            in_class = not in_class
        return pos + 1 if in_class else None

    def _char_in_class(self, ch: str, members: str) -> bool:
        i = 0
        while i < len(members):
            # range like a-z
            if i + 2 < len(members) and members[i + 1] == "-":
                if members[i] <= ch <= members[i + 2]:
                    return True
                i += 3
            elif members[i] == "\\" and i + 1 < len(members):
                escape_ch = members[i + 1]
                if escape_ch == "d" and ch.isdigit():
                    return True
                if escape_ch == "w" and (ch.isalnum() or ch == "_"):
                    return True
                if escape_ch == "s" and ch in " \t\n\r\f\v":
                    return True
                i += 2
            else:
                if ch == members[i]:
                    return True
                i += 1
        return False

    def _match_concat(self, node: ConcatNode, text: str, pos: int) -> Optional[int]:
        current = pos
        for child in node.children:
            result = self._match_node(child, text, current)
            if result is None:
                return None
            current = result
        return current

    def _match_alternation(
        self, node: AlternationNode, text: str, pos: int
    ) -> Optional[int]:
        for alt in node.alternatives:
            result = self._match_node(alt, text, pos)
            if result is not None:
                return result
        return None

    def _match_quantifier(
        self, node: QuantifierNode, text: str, pos: int
    ) -> Optional[int]:
        """
        A greedy quantifier matching with backtracking
        """
        return self._greedy_match(node, text, pos, 0)

    def _greedy_match(
        self, node: QuantifierNode, text: str, pos: int, count: int
    ) -> Optional[int]:
        if node.max is not None and count >= node.max:
            return pos

        result = self._match_node(node.child, text, pos)
        if result is not None and result != pos:
            # try a greedy consumption first
            deeper = self._greedy_match(node, text, result, count + 1)

            if deeper is not None:
                return deeper

            # backtrack: accept current count if it meets minimum
            if count + 1 >= node.min:
                return result

        # cant consume any more
        if count >= node.min:
            return pos
        return None

    def _match_group(self, node: GroupNode, text: str, pos: int) -> Optional[int]:
        end = self._match_node(node.child, text, pos)
        if end is not None:
            self._groups[node.group_index] = (pos, end)
        return end

    def _collect_groups(self, text: str) -> list[str]:
        if not self._groups:
            return []

        max_idx = max(self._groups.keys())
        return [
            text[self._groups[i][0] : self._groups[i][1]] if i in self._groups else ""
            for i in range(1, max_idx + 1)
        ]
