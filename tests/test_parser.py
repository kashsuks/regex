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
    NamedGroupNode,
    NonCapturingGroupNode,
    QuantifierNode,
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
