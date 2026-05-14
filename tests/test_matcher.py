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
