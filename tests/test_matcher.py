from helpers import make_match, make_all, spans

class TestNonCapturingAndNamedGroups:
    def test_non_capturing_group_matches(self):
        r = make_match("(?:abc)", "xabcy")
        assert r.matched and r.span == "abc"

    def test_non_capturing_group_not_in_grousp(self):
        r = make_match("(?:abc)", "xabcy")
        assert r.groups == []

    def test_non_capturing_with_quantifier(self):
        r = make_match("(?:ab)+", "ababab")
        assert r.matched and r.span == "ababab"

    def test_non_capturing_with_alternation(self):
        r = make_match("(?:cat|dog)s", "dogs")
        assert r.matched and r.span == "dogs"

    def test_named_group_matches(self):
        r = make_match(r"(?P<word>[a-z]+)", "hello")
        assert r.matched and r.span == "hello"

    def test_named_group_in_named_groups(self):
        r = make_match(r"(?P<word>[a-z]+)", "hello")
        assert r.named_groups == {"word": "hello"}

    def test_named_group_also_in_groups(self):
        r = make_match(r"(?P<word>[a-z]+)", "hello")
        assert r.groups == ["hello"]

    def test_two_named_groups(self):
        r = make_match(r"(?P<first>[a-z]+)\s(?P<second>[a-z]+)", "foo bar")
        assert r.named_groups == {"first": "foo", "second": "bar"}

    def test_mixed_capturing_and_non_capturing(self):
        r = make_match(r"(?:Mr|Ms)\s([A-Z][a-z]+)", "Mr Smith")
        assert r.matched
        assert r.groups == ["Smith"] # only the capturing group

class TestCaseInsensitive:
    def test_literal_upper(self):
        r = make_match("(?i)hello", "HELLO")
        assert r.matched and r.span == "HELLO"

    def test_literal_mixed(self):
        r = make_match("(?i)hello", "HeLLo")
        assert r.matched and r.span == "HeLLo"

    def test_without_flag_no_match(self):
        assert not make_match("hello", "HELLO").matched

    def test_char_class_case_insensitive(self):
        r = make_match("(?i)[a-z]+", "ABC")
        assert r.matched and r.span == "ABC"

    def test_flag_only_affects_its_scope(self):
        # (?i)foo matches FOO, but a subsequent plain pattern does not
        assert make_match("(?i)foo", "FOO").matched
        assert not make_match("foo", "FOO").matched

    def test_with_alternation(self):
        r = make_match("(?i)cat|dog", "CAT")
        assert r.matched and r.span == "CAT"

    def test_find_all_case_insensitive(self):
        results = spans("(?i)[a-z]+", "Hello WORLD foo")
        assert results == ["Hello", "WORLD", "foo"]

class TestLookahead:
    def test_positive_lookahead_matches(self):
        r = make_match(r"foo(?=bar)", "foobar")
        assert r.matched and r.span == "foo"

    def test_positive_lookahead_no_match(self):
        assert not make_match(r"foo(?=bar)", "foobaz").matched

    def test_positive_lookahead_does_not_consume(self):
        # the bar should still be available after the lookahead
        r = make_match(r"foo(?=bar)bar", "foobar")
        assert r.matched and r.span == "foobar"

    def test_negative_lookahead_matches(self):
        r = make_match(r"foo(?!bar)", "foobaz")
        assert r.matched and r.span == "foo"

    def test_negative_lookahead_no_match(self):
        assert not make_match(r"foo(?!bar)", "foobar").matched

    def test_lookahead_with_find_all(self):
        # match digits only if followed by px
        results = spans(r"\d+(?=px)", "10px 20em 30px")
        assert results == ["10", "30"]

class TestLookbehind:
    def test_positive_lookbehind_matches(self):
        # "bar" only if preceded by "foo"
        r = make_match(r"(?<=foo)bar", "foobar")
        assert r.matched and r.span == "bar"

    def test_positive_lookbehind_no_match(self):
        assert not make_match(r"(?<=foo)bar", "bazbar").matched

    def test_positive_lookbehind_does_not_consume(self):
        # foo should not be part of this span
        r = make_match(r"(?<=foo)bar", "foobar")
        assert r.span == "bar"
        assert r.start == 3

    def test_negative_lookbehind_no_match(self):
        assert not make_match(r"(?<!foo)bar", "foobar").matched

    def test_lookbehind_with_find_all(self):
        results = spans(r"(?<=\$)\d+", "cost $10 and $20 not 30")
        assert results == ["10", "20"]
