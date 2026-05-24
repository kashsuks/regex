import pytest
from regecks.engine.models import (
    ASTNode,
    AlternationNode,
    AnchorStartNode,
    AnchorEndNode,
    CharClassNode,
    ConcatNode,
    DotNode,
    EscapeNode,
    LiteralNode,
    GroupNode,
    LookbehindNode,
    LookaheadNode,
    NamedGroupNode,
    NonCapturingGroupNode,
    QuantifierNode,
    WordBoundaryNode,
)
from regecks.engine.parser import Parser, ParseError


def parse(pattern: str) -> ASTNode:
    return Parser(pattern).parse()


class TestNonCapturingAndNamedGroups:
    def test_non_capturing_group(self):
        node = parse("(?:abc)")
        assert isinstance(node, NonCapturingGroupNode)

    def test_non_capturing_not_a_group_node(self):
        node = parse("(?:abc)")
        assert not isinstance(node, GroupNode)

    def test_named_group(self):
        node = parse("(?P<foo>abc)")
        assert isinstance(node, NamedGroupNode)
        assert node.name == "foo"
        assert node.group_index == 1

    def test_named_group_empty_name_raises(self):
        with pytest.raises(ParseError):
            parse("(?P<>abc)")

    def test_non_capturing_does_not_increment_group_counter(self):
        # (?:a)(b) -> only one capturing group, index should be 1
        node = parse("(?:a)(b)")
        assert isinstance(node, ConcatNode)
        group = next(c for c in node.children if isinstance(c, GroupNode))
        assert group.group_index == 1


class TestLookaheadLookbehind:
    def test_positive_lookahead_node(self):
        node = parse(r"foo(?=bar)")
        assert isinstance(node, ConcatNode)
        la = node.children[-1]
        assert isinstance(la, LookaheadNode)
        assert la.positive is True

    def test_negative_lookahead_node(self):
        node = parse(r"foo(?!bar)")
        assert isinstance(node, ConcatNode)
        la = node.children[-1]
        assert isinstance(la, LookaheadNode)
        assert la.positive is False

    def test_positive_lookbehind_node(self):
        node = parse(r"(?<=foo)bar")
        assert isinstance(node, ConcatNode)
        lb = node.children[0]
        assert isinstance(lb, LookbehindNode)
        assert lb.positive is True

    def test_negative_lookbehind_node(self):
        node = parse(r"(?<!foo)bar")
        assert isinstance(node, ConcatNode)
        lb = node.children[0]
        assert isinstance(lb, LookbehindNode)
        assert lb.positive is False

    def test_lookahead_does_not_capture(self):
        # lookahead should not add to group counter
        node = parse(r"(a)(?=b)(c)")
        assert isinstance(node, ConcatNode)
        groups = [c for c in node.children if isinstance(c, GroupNode)]
        assert groups[0].group_index == 1
        assert groups[1].group_index == 2

class TestWordBoundary:
    def test_boundary_node_positive(self):
        node = parse(r"\b")
        assert isinstance(node, WordBoundaryNode)
        assert node.positive is True

    def test_boundary_node_negative(self):
        node = parse(r"\B")
        assert isinstance(node, WordBoundaryNode)
        assert node.positive is False

    def test_boundary_does_not_produce_escape_node(self):
        node = parse(r"\b")
        assert not isinstance(node, EscapeNode)

    def test_boundary_in_sequence(self):
        node = parse(r"\bfoo\b")
        assert isinstance(node, ConcatNode)
        assert isinstance(node.children[0], WordBoundaryNode)
        assert isinstance(node.children[-1], WordBoundaryNode)
