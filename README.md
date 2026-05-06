# cits5505-project

## Backend setup

Create and activate a virtual environment:

```bash
python3 -m venv application-env
source application-env/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask application:

```bash
python run.py
```

## Database setup

Apply database migrations:

```bash
flask --app run db upgrade
```

## Seed sample data

After applying database migrations, run:

```bash
python seed.py
```

This creates sample users, restaurants, menu items, opening hours, reviews, review photos, and bookmark collections for local development and testing.