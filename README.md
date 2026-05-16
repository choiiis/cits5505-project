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

Create a `.env` file in the project root. Keep this file private and never commit real secrets:

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

Run the Flask application:

```bash
python run.py
```

## Database setup

Apply database migrations:

```bash
flask --app run db upgrade
```

This creates the authentication token table and adds email verification tracking.

## Seed sample data

After applying database migrations, run:

```bash
python seed.py
```

This creates sample users, restaurants, menu items, opening hours, reviews, review photos, and bookmark collections for local development and testing.
