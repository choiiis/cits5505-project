# TableTrail Restaurant Review Application

## Purpose, Design, and Use

TableTrail is a Flask-based restaurant review web application for discovering, reviewing, saving, and managing restaurants. The application supports customer-facing restaurant discovery features as well as owner and admin workflows.

Users can browse the home page, search for restaurants, view restaurant detail pages, write reviews, save restaurants into bookmark collections, subscribe to public collections, and manage their profile. Restaurant owners can manage their own restaurant information, opening hours, menu items, and review reports. Admin pages provide management views for users, restaurants, and reviews.

The application is built with:

- Flask for the backend web framework and routing.
- Jinja templates for server-rendered pages.
- Flask-SQLAlchemy for database models.
- Flask-Migrate/Alembic for database migrations.
- SQLite for local development data storage.
- HTML, CSS, and JavaScript for the frontend interface.

## Group Members

| UWA ID | Name | GitHub username |
| --- | --- | --- |
| 24761125 | Heamin Choi | choiiis |
| 24806485 | Hongzhen Li | Max-Hongzhen2026 |
| 24577125 | Ashish Hareshbhai Narola | ashishreact |
| 24714078 | Celine Xu | 1031Celinela |

## Launch Instructions

1. Clone the public GitHub repository:

```bash
git clone <repository-url>
cd cits5505-project
```

2. Create and activate a virtual environment:

```bash
python3 -m venv application-env
source application-env/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root. Keep this file private and never commit real secrets:

```env
SECRET_KEY=replace-with-a-random-secret
DATABASE_URL=sqlite:///app.db
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail-address@gmail.com
SMTP_APP_PASSWORD=your-google-app-password
FRONTEND_URL=http://127.0.0.1:5000
EMAIL_FROM=your-gmail-address@gmail.com
EMAIL_OUTBOX_ENABLED=false
```

Use a long random value for `SECRET_KEY`; it protects sessions and CSRF tokens. The application will create a temporary development key if this value is missing, but that key changes on every restart and must not be used for deployment.

### Gmail App Password setup

The app sends email verification, password reset, and email-change links through Gmail SMTP.

1. Enable 2-Step Verification on the Google account that will send mail.
2. Open your Google Account settings, then go to **Security**.
3. Search for **App passwords**.
4. Create an app password for Mail.
5. Copy the 16-character app password into `SMTP_APP_PASSWORD` in `.env`.
6. Set `SMTP_USER` and `EMAIL_FROM` to the Gmail address used to create the app password.

`FRONTEND_URL` must match the URL users open in the browser, for example `http://127.0.0.1:5000` locally.

Set `EMAIL_OUTBOX_ENABLED=true` only for local development when you want outgoing email bodies and links written to `email_outbox.log`. Keep it disabled outside local testing because auth links contain sensitive one-time tokens.

5. Apply database migrations:

```bash
flask --app run db upgrade
```

6. Seed sample data:

```bash
python seed.py
```

This creates sample users, restaurants, menu items, opening hours, reviews, review photos, and bookmark collections for local development and testing.

7. Run the application:

```bash
python run.py
```

8. Open the application in a browser:

```text
http://127.0.0.1:5000
```

## Test Instructions

The project includes automated unit tests and Selenium WebDriver tests.

### Unit Tests

Unit tests test individual functions or small pieces of backend logic in isolation. They should be automated, repeatable, fast, limited in scope, and clear enough that a failing test points directly to the function that has broken.

Current unit test coverage includes:

- Utility functions such as star rating formatting.
- Login and password validation helpers.
- Review summary and restaurant rating calculation logic.
- Bookmark collection formatting logic.
- Database-backed helper behaviour using a temporary test database.

Database-backed unit tests use a temporary SQLite database created in `setUp()` and cleared in `tearDown()` so that each test starts from a known state and does not write to `app.db`.

Current structure:

```text
tests/
  test_utils.py
  test_auth_helpers.py
  test_review_helpers.py
  test_bookmark_helpers.py
```

Run unit tests with:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Selenium WebDriver Tests

Selenium WebDriver tests cover important browser workflows. These tests are slower than unit tests, so they focus on a representative selection of user journeys rather than every function.

Current Selenium coverage includes:

- Home page search form navigation to the search results page.
- Search results page rendering.
- Bookmark collections and public collections section rendering.
- Bookmark collection search filtering.
- Create collection modal opening.
- Search page collection picker opening for a logged-in seeded customer.
- Collection picker option selection.

Current structure:

```text
tests/
  selenium/
    base.py
    test_home_search.py
    test_bookmark_workflow.py
    test_search_collection_picker.py
```

The Selenium tests are skipped by default so that normal unit test runs do not require a browser driver.

Install Selenium if it is not already installed:

```bash
pip install selenium
```

Before running Selenium tests, start the Flask development server:

```bash
python run.py
```

Then run the Selenium test files from another terminal:

```bash
RUN_SELENIUM=1 python -m unittest discover -s tests/selenium -p "test_*.py"
```

The Selenium tests use Selenium WebDriver directly. They do not use Selenium IDE.

### Test Scope

The project is expected to include unit tests and Selenium WebDriver tests. It is not expected to include full integration tests, acceptance tests, test-driven design, Selenium IDE recordings, custom mocks/fakes/stubs, or GitHub workflow automation.