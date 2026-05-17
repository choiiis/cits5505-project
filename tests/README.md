# Test Suite

This directory contains automated tests for the TableTrail Flask application.

## Unit Tests

Run all unit tests from the project root:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

The unit tests cover utility functions, authentication helpers, review summary logic, restaurant rating refresh logic, and bookmark collection formatting. Database-backed unit tests use a temporary SQLite database and do not write to `app.db`.

## Selenium WebDriver Tests

The Selenium tests are stored in `tests/selenium/`. They are skipped by default so that normal unit test runs do not require a browser driver.

Install Selenium if it is not already installed:

```bash
pip install selenium
```

Start the Flask application in one terminal:

```bash
python run.py
```

Run Selenium tests from another terminal:

```bash
RUN_SELENIUM=1 python -m unittest discover -s tests/selenium -p "test_*.py"
```

Optional environment variables:

```bash
APP_BASE_URL=http://127.0.0.1:5000
SELENIUM_HEADLESS=1
```

The Selenium tests use Selenium WebDriver directly. They do not use Selenium IDE.

Current Selenium coverage includes:

- Home page search form navigation to the search results page.
- Search results page rendering.
- Bookmark collections and public collections section rendering.
- Bookmark collection search filtering.
- Create collection modal opening.
- Search page collection picker opening for a logged-in seeded customer.
- Collection picker option selection.
