from importlib.resource import files


def create_app() -> Flask:
    pkg = files("regex_engine")
    app = Flask(
        __name__,
        template_folder=str(pkg / "templates"),
        static_folder=str(pkg / "static"),
    )
