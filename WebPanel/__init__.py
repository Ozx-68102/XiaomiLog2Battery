import os
import secrets
import string

from flask import Flask

from WebPanel.models import db
from WebPanel.routes import bp as routes_bp


def generate_psk(length: int = 30) -> str:
    characters = string.ascii_letters + string.digits
    psk = ''.join(secrets.choice(characters) for _ in range(length))
    return psk


def create_app() -> Flask:
    app = Flask(__name__, static_url_path="/static", static_folder="static")

    os.makedirs(app.instance_path, exist_ok=True)
    database_path = os.path.join(app.instance_path, "database.db")

    app.config.update(
        SECRET_KEY=generate_psk(),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(routes_bp)

    return app
