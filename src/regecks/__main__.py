import sys
from venv import create


def main() -> None:
    args = sys.argv[1:]
    command = args[0] if args else "tui"

    if command == "web":
        from regecks.web.app import create_app

        app = create_app()
        app.run(debug=True, port=5000)

    elif command == "tui":
        from regecks.tui.app import RegexApp

        RegexApp().run()

    else:
        print(f"Unknown command: {command!r}")
        print("Usage: regecks [tui|web]")
        sys.exit(1)


if __name__ == "__main__":
    main()
