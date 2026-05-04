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