import os

basedir = os.path.abspath(os.path.dirname(__file__))

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(basedir, ".env"))
except ImportError:
    pass


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
