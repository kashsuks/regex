from importlib.resources import files

from flask import Flask

from .routes import main_bp


def create_app() -> Flask:
    pkg = files("regex_engine")
    app = Flask(
        __name__,
        template_folder=str(pkg / "templates"),
        static_folder=str(pkg / "static"),
    )
    app.register_blueprint(main_bp)
    return app
