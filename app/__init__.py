import os

from flask import Flask
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from config import Config

session = Session()


def create_app(config_class=Config):
    if not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL is not set")

    app = Flask(__name__)
    app.config.from_object(config_class)
    session.init_app(app)
    app.engine = create_engine(
        app.config.get("DATABASE_URL"))
    app.db = scoped_session(sessionmaker(bind=app.engine))
    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp)
    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app
