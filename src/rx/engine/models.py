from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class ASTNode:
    """
    Base case for all AST nodes
    """


@dataclass
class LiteralNode(ASTNode):
    char: str


@dataclass
class DotNode(ASTNode):
    """
    Matches any character except newline
    """


@dataclass
class AnchorStartNode(ASTNode):
    """
    Anchors match to start of string (^)
    """


@dataclass
class AnchorEndNode(ASTNode):
    """
    Anchors match to end of string ($)
    """


@dataclass
class EscapeNode(ASTNode):
    """
    Matches a character class shortand: \\d \\w \\s

    Also handles escaped literal like \\. \\* etc
    """

    sequence: str  # \\d, \\W, \\n


@dataclass
class CharClassNode(ASTNode):
    """
    Matches a character from a bracket expression

    negated is True for [^...]
    members is the raw inner string
    """

    members: str
    negated: bool


@dataclass
class ConcatNode(ASTNode):
    children: list[ASTNode] = field(default_factory=list)


@dataclass
class AlternationNode(ASTNode):
    alternatives: list[ASTNode] = field(default_factory=list)


@dataclass
class QuantifierNode(ASTNode):
    child: ASTNode
    min: int
    max: Optional[int]


@dataclass
class GroupNode(ASTNode):
    child: ASTNode
    group_index: int


@dataclass
class MatchResult:
    matched: bool
    start: int
    end: int
    span: str
    groups: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "matched": self.matched,
            "start": self.start,
            "end": self.end,
            "span": self.span,
            "groups": self.groups,
        }
