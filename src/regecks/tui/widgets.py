from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable, Static

from regecks.engine.models import MatchResult


class HighlightView(Widget):
    DEFAULT_CSS = """
    HighlightView {
        height: auto;
        min-height: 3;
        border: solid $surface-lighten-2;
        padding: 0 1;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("", id="highlight-text")

    def clear(self) -> None:
        self.query_one("#highlight-text", Static).update("")

    def show(self, text: str, results: list[MatchResult]) -> None:
        if not results:
            self.query_one("#highlight-text", Static).update(
                Text(text or "(empty)", style="dim")
            )
            return

        rich_text = Text()
        pos = 0
        for match in sorted(results, key=lambda r: r.start):
            if match.start > pos:
                rich_text.append(text[pos : match.start])
            rich_text.append(
                text[match.start : match.end], style="bold green on dark_green"
            )
            pos = match.end

        if pos < len(text):
            rich_text.append(text[pos:])

        self.query_one("#highlight-text", Static).update(rich_text)


class MatchTable(Widget):
    DEFAULT_CSS = """
    MatchTable {
        height: auto;
        min-height: 4;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        table: DataTable = DataTable(id="results-table", show_cursor=False)
        table.add_columns("#", "Match", "Start", "End", "Groups")
        yield table

    def clear_matches(self) -> None:
        self.query_one("#results-table", DataTable).clear()

    def show_matches(self, results: list[MatchResult]) -> None:
        table = self.query_one("#results-table", DataTable)
        table.clear()
        for i, r in enumerate(results, start=1):
            groups = ", ".join(r.groups) if r.groups else "-"
            table.add_row(str(i), r.span, str(r.start), str(r.end))
