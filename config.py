import os
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))


def load_local_env():
    env_path = os.path.join(basedir, ".env")

    if not os.path.exists(env_path):
        return

    with open(env_path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_local_env()


def require_env(name):
    value = os.environ.get(name)

    if not value:
        raise RuntimeError(
            f"{name} must be set in the environment or a private .env file."
        )

    return value


def get_secret_key():
    value = os.environ.get("SECRET_KEY")

    if value:
        return value

    if os.environ.get("FLASK_ENV") == "production":
        return require_env("SECRET_KEY")

    return secrets.token_hex(32)


class Config:
    SECRET_KEY = get_secret_key()
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_APP_PASSWORD = os.environ.get("SMTP_APP_PASSWORD", "")
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://127.0.0.1:5000")
    EMAIL_FROM = os.environ.get("EMAIL_FROM", SMTP_USER)
    EMAIL_OUTBOX_ENABLED = (
        os.environ.get("EMAIL_OUTBOX_ENABLED", "false").lower() == "true"
    )
