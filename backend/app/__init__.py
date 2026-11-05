"""API REST del Planificador Outdoor (Python + Flask + SQLite)."""
import os
from pathlib import Path

from flask import Flask, jsonify

from . import auth, perfiles, rutas, salidas
from .db import close_db, init_db


def create_app(config=None):
    app = Flask(__name__)
    raiz = Path(__file__).resolve().parent.parent
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "clave-de-desarrollo-cambiar-en-produccion"),
        DATABASE=os.environ.get("DATABASE", str(raiz / "planificador.db")),
        JSON_AS_ASCII=False,
    )
    if config:
        app.config.update(config)
    app.json.ensure_ascii = False

    app.teardown_appcontext(close_db)
    for modulo in (auth, perfiles, rutas, salidas):
        app.register_blueprint(modulo.bp)

    with app.app_context():
        init_db()

    @app.get("/api/salud")
    def salud():
        return jsonify({"estado": "ok"})

    return app
