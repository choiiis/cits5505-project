from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from app.security import get_csrf_token, validate_csrf_token

app = Flask(__name__)
app.config.from_object(Config)
app.before_request(validate_csrf_token)
app.context_processor(lambda: {"csrf_token": get_csrf_token})

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
