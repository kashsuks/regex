from flask import Blueprint, jsonify, render_template, request

from engine import Matcher
from engine.lexer import LexerError
from engine.parser import ParseError

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/api/match", methods=["POST"])
def api_match():
    """
    POST /api/match
    Body JSON: { "pattern": str, "text": str, "mode": "first"| "all"}

    Returns: { "results": [...], "error": null | str }
    """

    data = request.get_json(silent=True) or {}
    pattern = data.get("pattern", "")
    text = data.get("text", "")
    mode = data.get("mode", "first")

    if not pattern:
        return jsonify({"results": [], "error": "Pattern cannot be empty"})

    try:
        matcher = Matcher(pattern)
        if mode == "all":
            matches = matcher.find_all(text)
            results = [m.to_dict() for m in matches]
        else:
            m = matcher.match(text)
            results = [m.to_dict()] if m.matched else []

        return jsonify({"results": results, "error": None})

    except (LexerError, ParseError) as exc:
        return jsonify({"results": [], "error": str(exc)})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"results": [], "error": f"Unexpected error: {exc}"})
