import unittest
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app.models import AuthToken, User
from app.routes import (
    hash_token,
    is_strong_enough_password,
    is_valid_email,
    is_valid_login,
)


class AuthHelperTests(unittest.TestCase):
    def test_is_valid_email_accepts_standard_address(self):
        self.assertTrue(is_valid_email("student@example.com"))

    def test_is_valid_email_rejects_missing_domain(self):
        self.assertFalse(is_valid_email("student@"))

    def test_is_strong_enough_password_requires_six_characters(self):
        self.assertFalse(is_strong_enough_password("short"))
        self.assertTrue(is_strong_enough_password("longer"))

    def test_is_valid_login_accepts_correct_password_hash(self):
        user = User(
            email="user@example.com",
            username="User",
            password_hash=generate_password_hash("secret123"),
        )

        self.assertTrue(is_valid_login(user, "secret123"))

    def test_is_valid_login_rejects_wrong_password(self):
        user = User(
            email="user@example.com",
            username="User",
            password_hash=generate_password_hash("secret123"),
        )

        self.assertFalse(is_valid_login(user, "wrong-password"))

    def test_hash_token_is_repeatable_and_not_plaintext(self):
        first_hash = hash_token("abc123")
        second_hash = hash_token("abc123")

        self.assertEqual(first_hash, second_hash)
        self.assertNotEqual(first_hash, "abc123")
        self.assertEqual(len(first_hash), 64)

    def test_auth_token_expiry_property(self):
        expired_token = AuthToken(
            user_id=1,
            token_hash="hash",
            purpose="reset",
            expires_at=datetime.utcnow() - timedelta(seconds=1),
        )

        self.assertTrue(expired_token.is_expired)


if __name__ == "__main__":
    unittest.main()
