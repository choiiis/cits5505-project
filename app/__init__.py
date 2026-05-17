from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFError, CSRFProtect
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Security token expired. Please refresh and try again.",
                }
            ),
            400,
        )

    return "Security token expired. Please refresh and try again.", 400

from app import routes, models
