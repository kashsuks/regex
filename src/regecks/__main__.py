"""
Main entry point for the tui app
"""


def main() -> None:
    from regecks.tui.app import RegexApp

    RegexApp().run()
