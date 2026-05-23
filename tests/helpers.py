from regecks.engine import Matcher
from regecks.engine.models import MatchResult


def make_match(pattern: str, text: str) -> MatchResult:
    return Matcher(pattern).match(text)


def make_all(pattern: str, text: str) -> list[MatchResult]:
    return Matcher(pattern).find_all(text)


def spans(pattern: str, text: str) -> list[str]:
    return [r.span for r in make_all(pattern, text)]
