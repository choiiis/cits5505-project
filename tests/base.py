import os
import tempfile
import unittest

from app import app, db


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".sqlite")
        self.original_config = {
            "TESTING": app.config.get("TESTING"),
            "SQLALCHEMY_DATABASE_URI": app.config.get("SQLALCHEMY_DATABASE_URI"),
            "EMAIL_OUTBOX_ENABLED": app.config.get("EMAIL_OUTBOX_ENABLED"),
        }
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI=f"sqlite:///{self.db_path}",
            EMAIL_OUTBOX_ENABLED=False,
        )
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        app.config.update(self.original_config)
        os.close(self.db_fd)
        os.unlink(self.db_path)


class RouteTestCase(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.client = app.test_client()
