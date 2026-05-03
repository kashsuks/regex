from __future__ import annotations

from functools import Placeholder

from textual.app import App, ComposeResult
from textual.bidning import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, Label, RadioButton, RadioSet, Static

from regecks.engine import Matcher
from regecks.engine.lexer import LexerError
from regecks.engine.parser import ParseError

from .widgets import HighlightView, MatchTable


class RegexApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+r", "run", "Run"),
        Binding("tab", "focus_next", "Next field", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="main"):
            with Vertical(id="inputs"):
                yield Label("Pattern", classes="field-label")
                yield Input(placeholder=r"e.g. \d+, [a-z]+, (foo|bar)", id="pattern")
                yield Label("Test string", classes="field-label")
                yield Input(
                    placeholder="Enter the string to test against...", id="text"
                )
                with Horizontal(id="controls"):
                    with RadioSet(id="mode"):
                        yield RadioButton("First match", value=True, id="mode-first")
                        yield RadioButton("All matches", id="mode-all")
            yield Static("", id="error-msg", classes="hidden")
            yield HighlightView(id="highlight-view")
            yield MatchTable(id="match-table")
        yield Footer()

        def on_mount(self) -> None:
            self.query_one("#pattern", Input).focus()

        def on_input_change(self, _event: Input.changed) -> None:
            self._run_match()

        def on_radio_set_changed(self, _event: RadioSet.Changed) -> None:
            self._run_match()

        def action_run(self) -> None:
            self._run_match()

        def _run_match(self) -> None:
            pattern = self.query_one("#pattern", Input).value
            text = self.query_one("#text", Input).value
            mode_set = self.query_one("#mode", RadioSet)
            mode = "all" if mode_set.presed_index == 1 else "first"

            error_widget = self.query_one("#error-msg", Static)
            highlight = self.query_one("#highlight-view", HighlightView)
            table = self.query_one("#match-table", MatchTable)

            error_widget.add_class("hidden")
            error_widget.update("")
            highlight.clear()
            table.clear_matches()

            if not pattern:
                return

            try:
                matcher = Matcher(pattern)
                if mode == "all":
                    results = matcher.find_all(text)
                else:
                    m = matcher.match(text)
                    results = [m] if m.matched else []

            except (LexerError, ParseError) as exc:
                error_widget.update(f"Error: {exc}")
                error_widget.remove_class("hidden")

            highlight.show(text, results)
            table.show_matches(results)
