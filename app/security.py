import secrets
from hmac import compare_digest

from flask import abort, request, session

CSRF_SESSION_KEY = "_csrf_token"


def get_csrf_token():
    token = session.get(CSRF_SESSION_KEY)

    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token

    return token


def validate_csrf_token():
    if request.method != "POST":
        return

    session_token = session.get(CSRF_SESSION_KEY)
    submitted_token = request.form.get("csrf_token", "")

    if not session_token or not compare_digest(session_token, submitted_token):
        abort(400, description="Invalid CSRF token.")
