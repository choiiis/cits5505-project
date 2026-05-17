import hashlib
import os
import re
import secrets
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from urllib.parse import quote_plus
from uuid import uuid4

from flask import (
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from app import app, db
from app.utils import make_star_text
from app.models import (
    AuthToken,
    Bookmark,
    BookmarkCollection,
    CollectionSubscription,
    Restaurant,
    MenuItem,
    OpeningHour,
    Review,
    ReviewPhoto,
    User,
)
from sqlalchemy.orm import joinedload
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

DEFAULT_PROFILE_IMAGE = "https://ui-avatars.com/api/?name=TableTrail&background=dcfce7&color=15803d&bold=true"
DEFAULT_RESTAURANT_IMAGE = "images/restaurant-default.png"
DEFAULT_MENU_IMAGE = "images/menu-default.png"
PROFILE_IMAGE_UPLOAD_FOLDER = os.path.join(
    app.static_folder, "uploads", "profile_images"
)
OWNER_MENU_UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads", "menu_items")
REVIEW_PHOTO_UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads", "review_photos")
ALLOWED_PROFILE_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_MENU_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_REVIEW_PHOTO_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

SEARCH_MAP_COORDINATES = {
    "Perth CBD": {"lat": -31.9523, "lng": 115.8613},
    "Northbridge": {"lat": -31.9466, "lng": 115.8552},
    "Subiaco": {"lat": -31.9485, "lng": 115.8246},
    "Victoria Park": {"lat": -31.9762, "lng": 115.8960},
    "East Victoria Park": {"lat": -31.9889, "lng": 115.9025},
    "Fremantle": {"lat": -32.0569, "lng": 115.7439},
    "Cottesloe": {"lat": -31.9940, "lng": 115.7609},
    "South Perth": {"lat": -31.9805, "lng": 115.8677},
    "Nedlands": {"lat": -31.9813, "lng": 115.8069},
    "Wembley": {"lat": -31.9339, "lng": 115.8175},
    "Inglewood": {"lat": -31.9207, "lng": 115.8878},
    "Carlisle": {"lat": -31.9791, "lng": 115.9182},
    "Willetton": {"lat": -32.0521, "lng": 115.8870},
    "West Leederville": {"lat": -31.9415, "lng": 115.8339},
    "Mount Lawley": {"lat": -31.9340, "lng": 115.8717},
    "Leederville": {"lat": -31.9367, "lng": 115.8412},
    "Scarborough": {"lat": -31.8958, "lng": 115.7643},
    "Claremont": {"lat": -31.9811, "lng": 115.7799},
    "Crawley": {"lat": -31.9802, "lng": 115.8170},
    "Applecross": {"lat": -32.0166, "lng": 115.8350},
    "Booragoon": {"lat": -32.0390, "lng": 115.8320},
    "Cannington": {"lat": -32.0169, "lng": 115.9364},
    "Morley": {"lat": -31.8878, "lng": 115.8999},
    "Belmont": {"lat": -31.9638, "lng": 115.9345},
    "Hillarys": {"lat": -31.8064, "lng": 115.7405},
}
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
EMAIL_VERIFICATION_HOURS = 24
PASSWORD_RESET_HOURS = 1
EMAIL_CHANGE_HOURS = 24
RATE_LIMIT_WINDOWS = {
    "login": (8, 300),
    "signup": (5, 300),
    "forgot_password": (5, 300),
    "resend_verification": (3, 300),
    "change_email": (5, 300),
}


def is_valid_email(email):
    return bool(email and EMAIL_PATTERN.match(email))


def is_strong_enough_password(password):
    return bool(password and len(password) >= 6)


def check_rate_limit(key):
    limit, window_seconds = RATE_LIMIT_WINDOWS[key]
    now = datetime.utcnow().timestamp()
    bucket_key = f"rate_limit:{key}"
    attempts = [
        timestamp
        for timestamp in session.get(bucket_key, [])
        if now - timestamp < window_seconds
    ]

    if len(attempts) >= limit:
        session[bucket_key] = attempts
        return False

    attempts.append(now)
    session[bucket_key] = attempts
    return True


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_auth_token(user, purpose, expires_in, new_email=None):
    token = secrets.token_urlsafe(32)
    auth_token = AuthToken(
        user=user,
        token_hash=hash_token(token),
        purpose=purpose,
        new_email=new_email,
        expires_at=datetime.utcnow() + expires_in,
    )
    db.session.add(auth_token)
    return token


def get_auth_token(raw_token, purpose):
    if not raw_token:
        return None

    return AuthToken.query.filter_by(
        token_hash=hash_token(raw_token),
        purpose=purpose,
    ).first()


def retire_open_tokens(user, purpose):
    now = datetime.utcnow()
    AuthToken.query.filter_by(
        user_id=user.id,
        purpose=purpose,
        used_at=None,
    ).update({"used_at": now})


def make_absolute_url(endpoint, **values):
    frontend_url = current_app.config["FRONTEND_URL"].rstrip("/")
    return f"{frontend_url}{url_for(endpoint, **values)}"


def send_email(to_email, subject, body):
    smtp_host = current_app.config["SMTP_HOST"]
    smtp_port = current_app.config["SMTP_PORT"]
    smtp_user = current_app.config["SMTP_USER"]
    smtp_password = current_app.config["SMTP_APP_PASSWORD"].replace(" ", "")
    email_from = current_app.config["EMAIL_FROM"] or smtp_user

    if (
        not smtp_user
        or not smtp_password
        or not email_from
        or smtp_user.startswith("your-")
        or smtp_password.startswith("your-")
        or email_from.startswith("your-")
    ):
        current_app.logger.warning(
            "SMTP credentials are not configured; email not sent."
        )
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = email_from
    message["To"] = to_email
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="tabletrail.local")
    message.set_content(body)
    write_local_email_copy(to_email, subject, body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_password)
            smtp.send_message(message)
    except Exception:
        current_app.logger.exception("Unable to send email to %s", to_email)
        return False

    return True


def write_local_email_copy(to_email, subject, body):
    if not current_app.config.get("EMAIL_OUTBOX_ENABLED"):
        return

    outbox_path = os.path.join(current_app.root_path, "..", "email_outbox.log")

    with open(outbox_path, "a", encoding="utf-8") as outbox:
        outbox.write("\n" + "=" * 72 + "\n")
        outbox.write(f"To: {to_email}\n")
        outbox.write(f"Subject: {subject}\n")
        outbox.write(f"Date: {datetime.utcnow().isoformat()}Z\n\n")
        outbox.write(body)
        outbox.write("\n")


def send_verification_email(user):
    retire_open_tokens(user, "verify_email")
    token = create_auth_token(
        user,
        "verify_email",
        timedelta(hours=EMAIL_VERIFICATION_HOURS),
    )
    verification_url = make_absolute_url("verify_email", token=token)
    body = (
        f"Hi {user.username},\n\n"
        "Please verify your TableTrail account by opening this link:\n"
        f"{verification_url}\n\n"
        f"This link expires in {EMAIL_VERIFICATION_HOURS} hours.\n\n"
        "If you did not create this account, you can ignore this email."
    )
    return send_email(user.email, "Verify your TableTrail email", body)


def send_password_reset_email(user):
    retire_open_tokens(user, "reset_password")
    token = create_auth_token(
        user,
        "reset_password",
        timedelta(hours=PASSWORD_RESET_HOURS),
    )
    reset_url = make_absolute_url("reset_password", token=token)
    body = (
        f"Hi {user.username},\n\n"
        "Use this link to reset your TableTrail password:\n"
        f"{reset_url}\n\n"
        f"This link expires in {PASSWORD_RESET_HOURS} hour.\n\n"
        "If you did not request this, you can ignore this email."
    )
    return send_email(user.email, "Reset your TableTrail password", body)


def send_change_email_verification(user, new_email):
    retire_open_tokens(user, "change_email")
    token = create_auth_token(
        user,
        "change_email",
        timedelta(hours=EMAIL_CHANGE_HOURS),
        new_email=new_email,
    )
    change_url = make_absolute_url("verify_email_change", token=token)
    body = (
        f"Hi {user.username},\n\n"
        "Please confirm this new email address for your TableTrail account:\n"
        f"{change_url}\n\n"
        f"This link expires in {EMAIL_CHANGE_HOURS} hours.\n\n"
        "Your current email will stay active until you verify this one."
    )
    return send_email(new_email, "Confirm your new TableTrail email", body)


def build_openstreetmap_embed_url(restaurant):
    coordinates = SEARCH_MAP_COORDINATES.get(restaurant.suburb or "")

    if not coordinates:
        coordinates = {
            "lat": -31.9523 + (((restaurant.id * 17) % 40) - 20) / 1000,
            "lng": 115.8613 + (((restaurant.id * 29) % 40) - 20) / 1000,
        }

    lat = coordinates["lat"]
    lng = coordinates["lng"]
    bbox = f"{lng - 0.008},{lat - 0.006},{lng + 0.008},{lat + 0.006}"

    return (
        "https://www.openstreetmap.org/export/embed.html"
        f"?bbox={quote_plus(bbox)}"
        "&layer=mapnik"
        f"&marker={lat}%2C{lng}"
    )


def is_valid_login(user, password):
    if not user or not password:
        return False

    return check_password_hash(user.password_hash, password)


def build_review_summary(reviews):
    total_reviews = len(reviews)
    rating_counts = {star: 0 for star in range(1, 6)}

    for review in reviews:
        rating_counts[review.rating] += 1

    average_rating = (
        sum(review.rating for review in reviews) / total_reviews
        if total_reviews
        else 0.0
    )

    distribution = []

    for star in range(5, 0, -1):
        count = rating_counts[star]
        percentage = int((count / total_reviews) * 100) if total_reviews else 0

        distribution.append(
            {
                "stars": star,
                "count": count,
                "percentage": percentage,
            }
        )

    return {
        "average_rating": round(average_rating, 1),
        "total_reviews": total_reviews,
        "distribution": distribution,
    }


def refresh_restaurant_rating_summary(restaurant):
    visible_reviews = Review.query.filter(
        Review.restaurant_id == restaurant.id,
        Review.status != "hidden",
    ).all()

    review_count = len(visible_reviews)
    restaurant.review_count = review_count
    restaurant.average_rating = (
        round(sum(review.rating for review in visible_reviews) / review_count, 1)
        if review_count
        else 0.0
    )
    restaurant.updated_at = datetime.utcnow()


def get_profile_review_or_redirect(review_id):
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to manage your reviews.", "info")
        return None, redirect(url_for("login"))

    review = Review.query.get_or_404(review_id)

    if review.user_id != user_id:
        flash("You can only manage your own reviews.", "danger")
        return None, redirect(url_for("profile"))

    return review, None


def make_initials(username):
    parts = username.split()
    if not parts:
        return "TT"

    return "".join(part[0] for part in parts[:2]).upper()


def is_allowed_profile_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_PROFILE_IMAGE_EXTENSIONS
    )


def get_restaurant_image(restaurant):
    return (
        restaurant.thumbnail_image
        or restaurant.hero_image
        or url_for("static", filename=DEFAULT_RESTAURANT_IMAGE)
    )


def is_allowed_menu_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_MENU_IMAGE_EXTENSIONS
    )


def is_allowed_review_photo(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_REVIEW_PHOTO_EXTENSIONS
    )


def save_menu_image(file_storage):
    if not file_storage or not file_storage.filename:
        return ""

    original_filename = secure_filename(file_storage.filename)

    if not is_allowed_menu_image(original_filename):
        flash("Please choose a PNG, JPG, JPEG, GIF, or WebP menu image.", "danger")
        return None

    os.makedirs(OWNER_MENU_UPLOAD_FOLDER, exist_ok=True)

    extension = original_filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid4().hex}.{extension}"
    file_storage.save(os.path.join(OWNER_MENU_UPLOAD_FOLDER, filename))

    return f"uploads/menu_items/{filename}"


def save_review_photo(file_storage):
    original_filename = secure_filename(file_storage.filename)
    extension = original_filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid4().hex}.{extension}"

    os.makedirs(REVIEW_PHOTO_UPLOAD_FOLDER, exist_ok=True)
    file_storage.save(os.path.join(REVIEW_PHOTO_UPLOAD_FOLDER, filename))

    return url_for("static", filename=f"uploads/review_photos/{filename}")


def format_restaurant_card(restaurant, is_saved=True):
    rating = round(restaurant.average_rating or 0, 1)

    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "restaurant_id": restaurant.id,
        "category": restaurant.category,
        "location": restaurant.suburb or restaurant.address,
        "rating": rating,
        "star_text": make_star_text(rating),
        "review_count": restaurant.review_count,
        "description": restaurant.description,
        "image": get_restaurant_image(restaurant),
        "is_saved": is_saved,
    }


def get_collection_cover_image(collection):
    for bookmark in collection.bookmarks:
        if bookmark.restaurant:
            return get_restaurant_image(bookmark.restaurant)

    return url_for("static", filename=DEFAULT_RESTAURANT_IMAGE)


def format_bookmark_collection(
    collection,
    is_saved=True,
    is_subscribed=False,
    current_user_id=None,
):
    restaurants = [
        format_restaurant_card(bookmark.restaurant, is_saved=is_saved)
        for bookmark in collection.bookmarks
        if bookmark.restaurant and bookmark.restaurant.status == "approved"
    ]
    cover_image = get_collection_cover_image(collection)

    return {
        "id": collection.id,
        "name": collection.name,
        "visibility": "Public" if collection.is_public else "Private",
        "share_code": f"COL-{collection.id:04d}",
        "cover_image": cover_image,
        "image": cover_image,
        "restaurant_count": len(restaurants),
        "description": collection.description,
        "restaurants": restaurants,
        "creator": collection.user.username if collection.user else "TableTrail user",
        "subscriber_count": len(collection.subscriptions),
        "is_subscribed": is_subscribed,
        "is_owner": current_user_id == collection.user_id if current_user_id else False,
    }


def get_demo_user():
    user_id = session.get("user_id")

    if user_id:
        user = User.query.get(user_id)
        if user:
            return user

    return User.query.filter_by(role="customer").order_by(User.id).first()


def get_public_collection_cards(limit=None, current_user=None):
    collections = BookmarkCollection.query.filter_by(is_public=True).all()
    formatted_collections = [
        format_bookmark_collection(
            collection,
            is_subscribed=bool(
                current_user
                and any(
                    subscription.user_id == current_user.id
                    for subscription in collection.subscriptions
                )
            ),
            current_user_id=current_user.id if current_user else None,
        )
        for collection in collections
    ]

    formatted_collections.sort(
        key=lambda collection: (
            collection["subscriber_count"],
            collection["restaurant_count"],
        ),
        reverse=True,
    )

    return formatted_collections[:limit] if limit else formatted_collections


def build_home_context():
    home_categories = [
        row[0]
        for row in db.session.query(Restaurant.category)
        .filter(Restaurant.status == "approved")
        .distinct()
        .order_by(Restaurant.category)
        .limit(5)
        .all()
        if row[0]
    ]
    featured_restaurants = [
        format_restaurant_card(restaurant)
        for restaurant in Restaurant.query.filter_by(status="approved")
        .order_by(Restaurant.average_rating.desc(), Restaurant.review_count.desc())
        .limit(4)
        .all()
    ]
    public_collections = get_public_collection_cards(limit=3)

    return {
        "home_categories": home_categories,
        "featured_restaurants": featured_restaurants,
        "public_collections": public_collections,
    }


@app.route("/")
def home():
    return render_template("index.html", **build_home_context())


@app.route("/index")
def index():
    return render_template("index.html", **build_home_context())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not check_rate_limit("login"):
            flash(
                "Too many login attempts. Please wait a few minutes and try again.",
                "danger",
            )
            return render_template("login.html")

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if is_valid_login(user, password):
            if user.status == "suspended":
                flash("This account is suspended. Please contact support.", "danger")
                return render_template("login.html")

            if not user.is_email_verified:
                flash("Please verify your email before logging in.", "warning")
                return render_template("login.html", unverified_email=email)

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            flash(f"Welcome back, {user.username}.", "success")
            return redirect(url_for("restaurant_detail", restaurant_id=1))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        if not check_rate_limit("forgot_password"):
            flash(
                "Too many password reset requests. Please wait a few minutes and try again.",
                "danger",
            )
            return render_template("forgot_password.html")

        email = request.form.get("email", "").strip().lower()

        if not is_valid_email(email):
            flash("Please enter your email address.", "danger")
            return render_template("forgot_password.html")

        user = User.query.filter_by(email=email).first()

        if user:
            send_password_reset_email(user)
            db.session.commit()

        flash(
            "If an account exists, a reset link has been sent.",
            "success",
        )

    return render_template("forgot_password.html")


@app.route("/resend-verification", methods=["POST"])
def resend_verification():
    if not check_rate_limit("resend_verification"):
        flash(
            "Too many verification email requests. Please wait a few minutes and try again.",
            "danger",
        )
        return redirect(url_for("login"))

    email = request.form.get("email", "").strip().lower()
    user = User.query.filter_by(email=email).first() if is_valid_email(email) else None

    if user and not user.is_email_verified:
        send_verification_email(user)
        db.session.commit()

    flash("If the account needs verification, a new link has been sent.", "success")
    return redirect(url_for("login"))


@app.route("/verify-email")
def verify_email():
    token_value = request.args.get("token", "")
    token = get_auth_token(token_value, "verify_email")
    status = "danger"
    title = "Verification link problem"
    message = "This verification link is invalid."

    if token:
        if token.is_used:
            status = "info"
            title = "Email already verified"
            message = "This verification link has already been used."
        elif token.is_expired:
            token.used_at = datetime.utcnow()
            db.session.commit()
            title = "Verification link expired"
            message = "This verification link has expired. Please request a new verification email."
        elif token.user.is_email_verified:
            token.used_at = datetime.utcnow()
            db.session.commit()
            status = "info"
            title = "Email already verified"
            message = "Your email is already verified. You can log in."
        else:
            token.user.email_verified_at = datetime.utcnow()
            token.used_at = datetime.utcnow()
            db.session.commit()
            status = "success"
            title = "Email verified"
            message = "Your email has been verified. You can now log in."

    return render_template(
        "email_verification_result.html",
        status=status,
        title=title,
        message=message,
    )


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token_value = request.args.get("token", "") or request.form.get("token", "")
    token = get_auth_token(token_value, "reset_password")

    if not token:
        return render_template(
            "reset_password.html",
            token="",
            token_is_valid=False,
            token_message="This password reset link is invalid.",
        )

    if token.is_used:
        return render_template(
            "reset_password.html",
            token="",
            token_is_valid=False,
            token_message="This password reset link has already been used.",
        )

    if token.is_expired:
        token.used_at = datetime.utcnow()
        db.session.commit()
        return render_template(
            "reset_password.html",
            token="",
            token_is_valid=False,
            token_message="This password reset link has expired.",
        )

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not is_strong_enough_password(password):
            flash("Password must be at least 6 characters.", "danger")
            return render_template(
                "reset_password.html",
                token=token_value,
                token_is_valid=True,
            )

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template(
                "reset_password.html",
                token=token_value,
                token_is_valid=True,
            )

        token.user.password_hash = generate_password_hash(password)
        token.used_at = datetime.utcnow()
        db.session.commit()
        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template(
        "reset_password.html",
        token=token_value,
        token_is_valid=True,
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if not check_rate_limit("signup"):
            flash(
                "Too many signup attempts. Please wait a few minutes and try again.",
                "danger",
            )
            return render_template("signup.html")

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "customer")
        abn_number = request.form.get("abn_number", "").strip()
        contact_number = request.form.get("contact_number", "").strip()

        if not username or not is_valid_email(email) or not password:
            flash("Please complete all required fields.", "danger")
            return render_template("signup.html")

        if not is_strong_enough_password(password):
            flash("Password must be at least 6 characters.", "danger")
            return render_template("signup.html")

        if role not in ["customer", "owner"]:
            flash("Please choose a valid account role.", "danger")
            return render_template("signup.html")

        if role == "owner" and (not abn_number or not contact_number):
            flash("Please complete all restaurant owner details.", "danger")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("signup.html")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with that email already exists.", "danger")
            return render_template("signup.html")

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            abn_number=abn_number if role == "owner" else None,
            contact_number=contact_number if role == "owner" else None,
        )

        db.session.add(user)
        email_sent = send_verification_email(user)
        db.session.commit()

        if email_sent:
            flash(
                "Account created. Please check your email to verify your account before logging in.",
                "success",
            )
        else:
            flash(
                "Account created, but the verification email could not be sent. Please check SMTP settings and resend verification from login.",
                "warning",
            )
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to view your profile.", "info")
        return redirect(url_for("login"))

    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        profile_image_file = request.files.get("profile_image")

        if not username:
            flash("Please enter your username.", "danger")
            return redirect(url_for("profile"))

        if profile_image_file and profile_image_file.filename:
            original_filename = secure_filename(profile_image_file.filename)

            if not is_allowed_profile_image(original_filename):
                flash("Please choose a PNG, JPG, GIF, or WebP profile image.", "danger")
                return redirect(url_for("profile"))

            os.makedirs(PROFILE_IMAGE_UPLOAD_FOLDER, exist_ok=True)
            extension = original_filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid4().hex}.{extension}"
            profile_image_file.save(os.path.join(PROFILE_IMAGE_UPLOAD_FOLDER, filename))
            user.profile_image = url_for(
                "static", filename=f"uploads/profile_images/{filename}"
            )

        user.username = username
        db.session.commit()

        session["username"] = user.username
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    reviews = (
        Review.query.options(
            joinedload(Review.restaurant),
            joinedload(Review.photos),
        )
        .filter_by(user_id=user.id)
        .order_by(Review.created_at.desc())
        .all()
    )
    pending_email_token = (
        AuthToken.query.filter_by(
            user_id=user.id,
            purpose="change_email",
            used_at=None,
        )
        .order_by(AuthToken.created_at.desc())
        .first()
    )
    pending_new_email = (
        pending_email_token.new_email
        if pending_email_token and not pending_email_token.is_expired
        else None
    )

    return render_template(
        "profile.html",
        user=user,
        initials=make_initials(user.username),
        profile_image=user.profile_image,
        reviews=reviews,
        pending_new_email=pending_new_email,
    )


@app.route("/change-email", methods=["GET", "POST"])
def change_email():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to change your email.", "info")
        return redirect(url_for("login"))

    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        if not check_rate_limit("change_email"):
            flash(
                "Too many email change requests. Please wait a few minutes and try again.",
                "danger",
            )
            return render_template("change_email.html", user=user)

        new_email = request.form.get("new_email", "").strip().lower()
        current_password = request.form.get("current_password", "")

        if not is_valid_email(new_email):
            flash("Please enter a valid new email address.", "danger")
            return render_template("change_email.html", user=user)

        if new_email == user.email:
            flash("That is already your current email address.", "info")
            return render_template("change_email.html", user=user)

        if User.query.filter(User.email == new_email, User.id != user.id).first():
            flash("That email is already used by another account.", "danger")
            return render_template("change_email.html", user=user)

        if not check_password_hash(user.password_hash, current_password):
            flash("Current password is incorrect.", "danger")
            return render_template("change_email.html", user=user)

        email_sent = send_change_email_verification(user, new_email)
        db.session.commit()

        if email_sent:
            flash(
                "Please verify the new email address. Your current email remains active until then.",
                "success",
            )
        else:
            flash(
                "The email change is pending, but the verification email could not be sent. Please check SMTP settings and try again.",
                "warning",
            )
        return redirect(url_for("profile"))

    return render_template("change_email.html", user=user)


@app.route("/verify-email-change")
def verify_email_change():
    token_value = request.args.get("token", "")
    token = get_auth_token(token_value, "change_email")
    status = "danger"
    title = "Email change link problem"
    message = "This email change link is invalid."

    if token:
        if token.is_used:
            status = "info"
            title = "Email change already handled"
            message = "This email change link has already been used."
        elif token.is_expired:
            token.used_at = datetime.utcnow()
            db.session.commit()
            title = "Email change link expired"
            message = (
                "This email change link has expired. Please request a new email change."
            )
        elif (
            not token.new_email
            or User.query.filter(
                User.email == token.new_email,
                User.id != token.user_id,
            ).first()
        ):
            token.used_at = datetime.utcnow()
            db.session.commit()
            title = "Email no longer available"
            message = "That email address is no longer available."
        else:
            token.user.email = token.new_email
            token.user.email_verified_at = datetime.utcnow()
            token.used_at = datetime.utcnow()
            db.session.commit()
            status = "success"
            title = "Email changed"
            message = "Your email address has been updated."

    return render_template(
        "email_verification_result.html",
        status=status,
        title=title,
        message=message,
    )


@app.route("/profile/reviews/<int:review_id>/edit", methods=["POST"])
def edit_profile_review(review_id):
    review, response = get_profile_review_or_redirect(review_id)

    if response:
        return response

    rating_text = request.form.get("rating", "").strip()
    content = request.form.get("content", "").strip()

    try:
        rating = int(rating_text)
    except ValueError:
        rating = 0

    if rating < 1 or rating > 5 or not content:
        flash("Please choose a rating and write your review.", "danger")
        return redirect(url_for("profile"))

    review.rating = rating
    review.content = content
    review.updated_at = datetime.utcnow()

    refresh_restaurant_rating_summary(review.restaurant)

    db.session.commit()

    flash("Review updated successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/profile/reviews/<int:review_id>/delete", methods=["POST"])
def delete_profile_review(review_id):
    review, response = get_profile_review_or_redirect(review_id)

    if response:
        return response

    restaurant = review.restaurant

    db.session.delete(review)
    db.session.flush()

    refresh_restaurant_rating_summary(restaurant)

    db.session.commit()

    flash("Review deleted successfully.", "success")
    return redirect(url_for("profile"))

    review.rating = rating
    review.content = content
    review.updated_at = datetime.utcnow()

    refresh_restaurant_rating_summary(review.restaurant)

    db.session.commit()

    flash("Review updated successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/search")
def search():
    keyword = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    category = request.args.get("category", "").strip()
    filter_location = request.args.get("filter_location", "").strip()
    rating = request.args.get("rating", "").strip()
    sort = request.args.get("sort", "rating").strip()
    active_location = filter_location or location

    query = Restaurant.query.filter(Restaurant.status == "approved")

    if keyword:
        search_text = f"%{keyword}%"

        query = (
            query.outerjoin(MenuItem)
            .filter(
                db.or_(
                    Restaurant.name.ilike(search_text),
                    Restaurant.category.ilike(search_text),
                    Restaurant.description.ilike(search_text),
                    MenuItem.name.ilike(search_text),
                    MenuItem.description.ilike(search_text),
                )
            )
            .distinct()
        )

    if filter_location:
        query = query.filter(Restaurant.suburb == filter_location)
    elif location:
        location_text = f"%{location}%"
        query = query.filter(
            db.or_(
                Restaurant.suburb.ilike(location_text),
                Restaurant.address.ilike(location_text),
            )
        )

    if category:
        query = query.filter(Restaurant.category == category)

    if rating:
        try:
            min_rating = float(rating)
            query = query.filter(Restaurant.average_rating >= min_rating)
        except ValueError:
            pass

    if sort == "reviews":
        query = query.order_by(Restaurant.review_count.desc())
    elif sort == "newest":
        query = query.order_by(Restaurant.created_at.desc())
    else:
        query = query.order_by(Restaurant.average_rating.desc())

    restaurants = query.all()

    summary_parts = [keyword if keyword else "restaurants"]

    if active_location:
        summary_parts.append(f"in {active_location}")

    if category:
        summary_parts.append(category)

    if rating:
        summary_parts.append(f"{rating}+ rating")

    search_summary_label = " ".join(summary_parts)

    categories = [
        row[0]
        for row in db.session.query(Restaurant.category)
        .distinct()
        .order_by(Restaurant.category)
        .all()
        if row[0]
    ]

    locations = [
        row[0]
        for row in db.session.query(Restaurant.suburb)
        .distinct()
        .order_by(Restaurant.suburb)
        .all()
        if row[0]
    ]
    user = get_demo_user()
    collection_choices = []
    saved_collection_ids_by_restaurant = {}

    if user:
        user_collection_ids = [
            collection.id
            for collection in BookmarkCollection.query.filter_by(user_id=user.id).all()
        ]
        collection_choices = [
            {
                "id": collection.id,
                "name": collection.name,
                "visibility": "Public" if collection.is_public else "Private",
            }
            for collection in BookmarkCollection.query.filter_by(user_id=user.id)
            .order_by(BookmarkCollection.created_at, BookmarkCollection.id)
            .all()
        ]

        if user_collection_ids:
            bookmarks = Bookmark.query.filter(
                Bookmark.collection_id.in_(user_collection_ids)
            ).all()
            for bookmark in bookmarks:
                saved_collection_ids_by_restaurant.setdefault(
                    bookmark.restaurant_id,
                    [],
                ).append(bookmark.collection_id)

    return render_template(
        "search.html",
        restaurants=restaurants,
        categories=categories,
        locations=locations,
        default_restaurant_image=DEFAULT_RESTAURANT_IMAGE,
        search_summary_label=search_summary_label,
        collection_choices=collection_choices,
        saved_collection_ids_by_restaurant=saved_collection_ids_by_restaurant,
    )


@app.route("/bookmarks")
def bookmarks():
    user = get_demo_user()
    user_collections = []
    subscribed_collections = []

    if user:
        user_collections = (
            BookmarkCollection.query.filter_by(user_id=user.id)
            .order_by(BookmarkCollection.created_at, BookmarkCollection.id)
            .all()
        )
        subscribed_collections = [
            subscription.collection
            for subscription in user.collection_subscriptions
            if subscription.collection
            and subscription.collection.is_public
            and subscription.collection.user_id != user.id
        ]

    favorite_collection = next(
        (
            collection
            for collection in user_collections
            if collection.name.lower() == "favorite"
        ),
        user_collections[0] if user_collections else None,
    )
    saved_restaurants = []

    if favorite_collection:
        saved_restaurants = [
            format_restaurant_card(bookmark.restaurant)
            for bookmark in favorite_collection.bookmarks
            if bookmark.restaurant and bookmark.restaurant.status == "approved"
        ]

    bookmark_collections = [
        format_bookmark_collection(
            collection, current_user_id=user.id if user else None
        )
        for collection in user_collections
    ]
    bookmark_collections.extend(
        format_bookmark_collection(
            collection,
            is_subscribed=True,
            current_user_id=user.id if user else None,
        )
        for collection in subscribed_collections
    )
    public_collections = get_public_collection_cards(current_user=user)

    return render_template(
        "bookmarks.html",
        saved_restaurants=saved_restaurants,
        bookmark_collections=bookmark_collections,
        public_collections=public_collections,
    )


@app.route("/collections/create", methods=["POST"])
def create_collection():
    user_id = session.get("user_id")

    if not user_id:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Please log in to create a collection.",
                    "redirect_url": url_for("login"),
                }
            ),
            401,
        )

    data = request.get_json(silent=True) or request.form
    name = data.get("name", "").strip()
    visibility = data.get("visibility", "Public").strip()

    if not name:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Please enter a collection name.",
                }
            ),
            400,
        )

    if visibility not in {"Public", "Private"}:
        visibility = "Public"

    existing_collection = BookmarkCollection.query.filter_by(
        user_id=user_id,
        name=name,
    ).first()

    if existing_collection:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "You already have a collection with that name.",
                }
            ),
            409,
        )

    collection = BookmarkCollection(
        user_id=user_id,
        name=name,
        description="Start adding saved restaurants to this collection.",
        is_public=visibility == "Public",
    )

    db.session.add(collection)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Collection created.",
            "collection": format_bookmark_collection(
                collection,
                current_user_id=user_id,
            ),
            "redirect_url": url_for("bookmarks") + "#collectionsTitle",
        }
    )


@app.route("/restaurants/<int:restaurant_id>/collections", methods=["POST"])
def update_restaurant_collections(restaurant_id):
    user_id = session.get("user_id")

    if not user_id:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Please log in to save restaurants.",
                    "redirect_url": url_for("login"),
                }
            ),
            401,
        )

    Restaurant.query.get_or_404(restaurant_id)
    data = request.get_json(silent=True) or {}
    selected_collection_ids = {
        int(collection_id)
        for collection_id in data.get("collection_ids", [])
        if str(collection_id).isdigit()
    }

    owned_collections = BookmarkCollection.query.filter_by(user_id=user_id).all()
    owned_collection_ids = {collection.id for collection in owned_collections}
    selected_collection_ids = selected_collection_ids & owned_collection_ids

    existing_bookmarks = (
        Bookmark.query.filter(
            Bookmark.restaurant_id == restaurant_id,
            Bookmark.collection_id.in_(owned_collection_ids),
        ).all()
        if owned_collection_ids
        else []
    )
    existing_collection_ids = {
        bookmark.collection_id for bookmark in existing_bookmarks
    }

    for collection_id in selected_collection_ids - existing_collection_ids:
        db.session.add(
            Bookmark(
                collection_id=collection_id,
                restaurant_id=restaurant_id,
            )
        )

    for bookmark in existing_bookmarks:
        if bookmark.collection_id not in selected_collection_ids:
            db.session.delete(bookmark)

    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Restaurant collections updated.",
            "collection_ids": sorted(selected_collection_ids),
        }
    )


@app.route("/collections/<int:collection_id>/subscribe", methods=["POST"])
def subscribe_collection(collection_id):
    user_id = session.get("user_id")

    if not user_id:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Please log in to subscribe to a collection.",
                    "redirect_url": url_for("login"),
                }
            ),
            401,
        )

    collection = BookmarkCollection.query.get_or_404(collection_id)

    if not collection.is_public:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Only public collections can be subscribed to.",
                }
            ),
            403,
        )

    if collection.user_id == user_id:
        return jsonify(
            {
                "success": True,
                "message": "This is your own collection.",
                "subscriber_count": len(collection.subscriptions),
                "redirect_url": url_for("bookmarks") + "#collectionsTitle",
            }
        )

    subscription = CollectionSubscription.query.filter_by(
        collection_id=collection.id,
        user_id=user_id,
    ).first()

    if not subscription:
        db.session.add(
            CollectionSubscription(
                collection_id=collection.id,
                user_id=user_id,
            )
        )
        db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Collection subscribed.",
            "subscriber_count": len(collection.subscriptions),
            "redirect_url": url_for("bookmarks", subscribed_collection=collection.id)
            + "#collectionsTitle",
        }
    )


@app.route("/restaurants/<int:restaurant_id>", methods=["GET", "POST"])
def restaurant_detail(restaurant_id):
    # restaurant summary
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if request.method == "POST":
        user_id = session.get("user_id")

        if not user_id:
            flash("Please log in to write a review.", "info")
            return redirect(url_for("login"))

        rating_text = request.form.get("rating", "").strip()
        review_text = request.form.get("review_text", "").strip()

        try:
            rating = int(rating_text)
        except ValueError:
            rating = 0

        if rating < 1 or rating > 5 or not review_text:
            flash("Please choose a rating and write your review.", "danger")
            return redirect(url_for("restaurant_detail", restaurant_id=restaurant.id))

        review_photo_files = [
            file_storage
            for file_storage in request.files.getlist("review_photos")
            if file_storage and file_storage.filename
        ]

        for file_storage in review_photo_files:
            original_filename = secure_filename(file_storage.filename)

            if not is_allowed_review_photo(original_filename):
                flash(
                    "Please choose PNG, JPG, JPEG, GIF, or WebP review photos.",
                    "danger",
                )
                return redirect(
                    url_for("restaurant_detail", restaurant_id=restaurant.id)
                )

        review = Review(
            restaurant_id=restaurant.id,
            user_id=user_id,
            rating=rating,
            content=review_text,
        )

        db.session.add(review)
        db.session.flush()

        for file_storage in review_photo_files:
            db.session.add(
                ReviewPhoto(
                    review_id=review.id,
                    image_url=save_review_photo(file_storage),
                )
            )

        visible_reviews = Review.query.filter(
            Review.restaurant_id == restaurant.id,
            Review.status != "hidden",
        ).all()

        restaurant.review_count = len(visible_reviews)
        restaurant.average_rating = round(
            sum(item.rating for item in visible_reviews) / restaurant.review_count,
            1,
        )
        restaurant.updated_at = datetime.utcnow()

        db.session.commit()
        flash("Review submitted successfully.", "success")
        return redirect(url_for("restaurant_detail", restaurant_id=restaurant.id))

    # restaurant opening hours
    opening_hours = (
        OpeningHour.query.filter_by(restaurant_id=restaurant.id)
        .order_by(OpeningHour.day_of_week)
        .all()
    )

    today_day_of_week = datetime.today().weekday()

    # restaurant menu highlights
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).all()

    reviews = (
        Review.query.filter(
            Review.restaurant_id == restaurant.id,
            Review.status != "hidden",
        )
        .order_by(Review.created_at.desc())
        .all()
    )

    current_user = None

    if session.get("user_id"):
        current_user = User.query.get(session["user_id"])

    review_summary = build_review_summary(reviews)
    star_text = make_star_text(review_summary["average_rating"])
    restaurant_map_embed_url = build_openstreetmap_embed_url(restaurant)

    return render_template(
        "restaurant_detail.html",
        restaurant=restaurant,
        opening_hours=opening_hours,
        menu_items=menu_items,
        review_summary=review_summary,
        reviews=reviews,
        star_text=star_text,
        today_day_of_week=today_day_of_week,
        is_logged_in="user_id" in session,
        current_user=current_user,
        default_profile_image=DEFAULT_PROFILE_IMAGE,
        default_restaurant_image=DEFAULT_RESTAURANT_IMAGE,
        default_menu_image=DEFAULT_MENU_IMAGE,
        restaurant_map_embed_url=restaurant_map_embed_url,
    )


@app.route("/restaurants/<int:restaurant_id>/menu")
def restaurant_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    return render_template("restaurant_menu.html", restaurant=restaurant)


def get_admin_user_or_redirect():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to access the admin dashboard.", "info")
        return None, redirect(url_for("login"))

    current_user = User.query.get_or_404(user_id)

    if current_user.role != "admin":
        flash("You do not have permission to access the admin dashboard.", "danger")
        return None, redirect(url_for("home"))

    return current_user, None


def redirect_back_to_admin():
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin")
def admin_dashboard():
    current_user, response = get_admin_user_or_redirect()

    if response:
        return response

    restaurant_status = request.args.get("restaurant_status", "").strip()
    restaurant_q = request.args.get("restaurant_q", "").strip()
    restaurant_sort = request.args.get("restaurant_sort", "recent").strip()

    user_status = request.args.get("user_status", "").strip()
    user_q = request.args.get("user_q", "").strip()
    user_sort = request.args.get("user_sort", "recent").strip()

    review_status = request.args.get("review_status", "").strip()
    review_q = request.args.get("review_q", "").strip()
    review_sort = request.args.get("review_sort", "recent").strip()

    overview_cards = [
        {"label": "Total Users", "value": User.query.count()},
        {"label": "Total Restaurants", "value": Restaurant.query.count()},
        {
            "label": "Pending Restaurants",
            "value": Restaurant.query.filter_by(status="pending").count(),
        },
        {
            "label": "Suspended Users",
            "value": User.query.filter_by(status="suspended").count(),
        },
    ]

    restaurant_query = Restaurant.query.outerjoin(User, Restaurant.owner_id == User.id)

    if restaurant_status:
        restaurant_query = restaurant_query.filter(
            Restaurant.status == restaurant_status
        )

    if restaurant_q:
        search_text = f"%{restaurant_q}%"
        restaurant_query = restaurant_query.filter(
            db.or_(
                Restaurant.name.ilike(search_text),
                Restaurant.category.ilike(search_text),
                Restaurant.suburb.ilike(search_text),
                Restaurant.address.ilike(search_text),
                User.username.ilike(search_text),
                User.email.ilike(search_text),
            )
        )

    if restaurant_sort == "oldest":
        restaurant_query = restaurant_query.order_by(Restaurant.created_at.asc())
    else:
        restaurant_query = restaurant_query.order_by(Restaurant.created_at.desc())

    restaurants = restaurant_query.limit(5).all()

    user_query = User.query

    if user_status:
        user_query = user_query.filter(User.status == user_status)

    if user_q:
        search_text = f"%{user_q}%"
        user_query = user_query.filter(
            db.or_(
                User.username.ilike(search_text),
                User.email.ilike(search_text),
                User.role.ilike(search_text),
            )
        )

    if user_sort == "oldest":
        user_query = user_query.order_by(User.created_at.asc())
    else:
        user_query = user_query.order_by(User.created_at.desc())

    users = user_query.limit(5).all()

    review_query = Review.query.join(
        Restaurant, Review.restaurant_id == Restaurant.id
    ).join(User, Review.user_id == User.id)

    if review_status:
        review_query = review_query.filter(Review.status == review_status)

    if review_q:
        search_text = f"%{review_q}%"
        review_query = review_query.filter(
            db.or_(
                Review.content.ilike(search_text),
                Restaurant.name.ilike(search_text),
                User.username.ilike(search_text),
                User.email.ilike(search_text),
            )
        )

    if review_sort == "oldest":
        review_query = review_query.order_by(Review.created_at.asc())
    elif review_sort == "highest_rating":
        review_query = review_query.order_by(
            Review.rating.desc(), Review.created_at.desc()
        )
    elif review_sort == "lowest_rating":
        review_query = review_query.order_by(
            Review.rating.asc(), Review.created_at.desc()
        )
    else:
        review_query = review_query.order_by(Review.created_at.desc())

    reviews = review_query.limit(5).all()

    return render_template(
        "admin_dashboard.html",
        overview_cards=overview_cards,
        restaurants=restaurants,
        users=users,
        reviews=reviews,
        restaurant_status=restaurant_status,
        restaurant_q=restaurant_q,
        restaurant_sort=restaurant_sort,
        user_status=user_status,
        user_q=user_q,
        user_sort=user_sort,
        review_status=review_status,
        review_q=review_q,
        review_sort=review_sort,
    )


@app.route("/admin/restaurants/update", methods=["POST"])
def update_restaurant_records():
    current_user, response = get_admin_user_or_redirect()

    if response:
        return response

    allowed_statuses = ["approved", "pending", "reported"]

    for key, value in request.form.items():
        if not key.startswith("restaurant_status_"):
            continue

        restaurant_id = key.replace("restaurant_status_", "")

        if not restaurant_id.isdigit():
            continue

        if value not in allowed_statuses:
            continue

        restaurant = Restaurant.query.get(int(restaurant_id))

        if restaurant:
            restaurant.status = value
            restaurant.updated_at = datetime.utcnow()

    db.session.commit()
    flash("Restaurant records updated.", "success")

    return redirect_back_to_admin()


@app.route("/admin/users/update", methods=["POST"])
def update_user_records():
    current_user, response = get_admin_user_or_redirect()

    if response:
        return response

    allowed_roles = ["customer", "owner", "admin"]
    allowed_statuses = ["active", "suspended"]

    user_ids = set()

    for key in request.form:
        if key.startswith("user_role_"):
            user_ids.add(key.replace("user_role_", ""))
        elif key.startswith("user_status_"):
            user_ids.add(key.replace("user_status_", ""))

    for user_id in user_ids:
        if not user_id.isdigit():
            continue

        user = User.query.get(int(user_id))

        if not user:
            continue

        role = request.form.get(f"user_role_{user.id}")
        status = request.form.get(f"user_status_{user.id}")

        if role in allowed_roles:
            user.role = role

        if status in allowed_statuses:
            if user.id == current_user.id and status == "suspended":
                flash("You cannot suspend your own admin account.", "danger")
                continue

            user.status = status

        user.updated_at = datetime.utcnow()

    db.session.commit()
    flash("User records updated.", "success")

    return redirect_back_to_admin()


@app.route("/admin/reviews/update", methods=["POST"])
def update_review_records():
    current_user, response = get_admin_user_or_redirect()

    if response:
        return response

    allowed_statuses = ["active", "reported", "hidden"]

    for key, value in request.form.items():
        if not key.startswith("review_status_"):
            continue

        review_id = key.replace("review_status_", "")

        if not review_id.isdigit():
            continue

        if value not in allowed_statuses:
            continue

        review = Review.query.get(int(review_id))

        if review:
            review.status = value
            review.updated_at = datetime.utcnow()

    db.session.commit()
    flash("Review records updated.", "success")

    return redirect_back_to_admin()


@app.route("/admin/reviews/<int:review_id>/delete", methods=["POST"])
def delete_review_record(review_id):
    current_user, response = get_admin_user_or_redirect()

    if response:
        return response

    review = Review.query.get_or_404(review_id)
    restaurant = review.restaurant

    db.session.delete(review)
    db.session.commit()

    remaining_reviews = Review.query.filter_by(restaurant_id=restaurant.id).all()
    total_reviews = len(remaining_reviews)

    restaurant.review_count = total_reviews
    restaurant.average_rating = (
        round(sum(item.rating for item in remaining_reviews) / total_reviews, 1)
        if total_reviews
        else 0.0
    )
    restaurant.updated_at = datetime.utcnow()

    db.session.commit()

    flash("Review deleted successfully.", "success")
    return redirect_back_to_admin()


def get_owner_user_or_redirect():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to access the owner dashboard.", "info")
        return None, redirect(url_for("login"))

    current_user = User.query.get_or_404(user_id)

    if current_user.role != "owner":
        flash("You do not have permission to access the owner dashboard.", "danger")
        return None, redirect(url_for("home"))

    return current_user, None


def get_owner_restaurants(current_user):
    return sorted(
        current_user.owned_restaurants,
        key=lambda restaurant: (restaurant.name or "").lower(),
    )


def get_owner_restaurant_or_redirect(current_user, restaurant_id=None):
    owner_restaurants = get_owner_restaurants(current_user)

    if not owner_restaurants:
        flash("No restaurant is linked to your owner account yet.", "info")
        return None, redirect(url_for("home"))

    if restaurant_id:
        restaurant = next(
            (item for item in owner_restaurants if item.id == restaurant_id),
            None,
        )

        if restaurant:
            return restaurant, None

        flash("You do not have permission to manage that restaurant.", "danger")
        return None, redirect(url_for("owner_dashboard"))

    return owner_restaurants[0], None


def get_selected_owner_restaurant(current_user):
    restaurant_id_text = (
        request.form.get("restaurant_id") or request.args.get("restaurant_id") or ""
    ).strip()

    restaurant_id = int(restaurant_id_text) if restaurant_id_text.isdigit() else None
    return get_owner_restaurant_or_redirect(current_user, restaurant_id)


def redirect_back_to_owner(restaurant_id=None):
    if restaurant_id:
        return redirect(url_for("owner_dashboard", restaurant_id=restaurant_id))

    return redirect(url_for("owner_dashboard"))


def format_time_for_input(value):
    if not value:
        return ""

    value = str(value).strip()

    for date_format in ("%H:%M", "%H:%M:%S", "%I:%M %p"):
        try:
            return datetime.strptime(value, date_format).strftime("%H:%M")
        except ValueError:
            pass

    return value[:5] if len(value) >= 5 else value


def build_owner_opening_hours(restaurant):
    return [
        {
            "id": hour.id,
            "day_label": hour.day_label,
            "open_time": format_time_for_input(hour.open_time),
            "close_time": format_time_for_input(hour.close_time),
            "is_closed": hour.is_closed,
        }
        for hour in sorted(restaurant.opening_hours, key=lambda item: item.day_of_week)
    ]


def build_owner_restaurant_info(restaurant):
    return [
        {"label": "Restaurant Name", "value": restaurant.name or ""},
        {"label": "Category", "value": restaurant.category or ""},
        {"label": "Address", "value": restaurant.address or ""},
        {"label": "Suburb", "value": restaurant.suburb or ""},
        {"label": "Phone", "value": restaurant.phone or ""},
        {"label": "Website", "value": restaurant.website or ""},
    ]


@app.route("/owner")
def owner_dashboard():
    current_user, response = get_owner_user_or_redirect()

    if response:
        return response

    restaurant, response = get_selected_owner_restaurant(current_user)

    if response:
        return response

    owner_restaurants = get_owner_restaurants(current_user)
    menu_items = sorted(
        restaurant.menu_items,
        key=lambda item: item.created_at or datetime.min,
        reverse=True,
    )

    reviews = sorted(
        restaurant.reviews,
        key=lambda item: item.created_at or datetime.min,
        reverse=True,
    )

    owner_stats = [
        {"label": "Restaurant", "value": restaurant.name},
        {"label": "Listing Status", "value": restaurant.status.title()},
        {"label": "Rating", "value": f"{restaurant.average_rating:.1f}"},
        {"label": "Reviews", "value": restaurant.review_count},
    ]

    return render_template(
        "owner_dashboard.html",
        restaurant=restaurant,
        owner_restaurants=owner_restaurants,
        owner_stats=owner_stats,
        reviews=reviews,
        restaurant_info=build_owner_restaurant_info(restaurant),
        opening_hours=build_owner_opening_hours(restaurant),
        menu_items=menu_items,
        default_menu_image=DEFAULT_MENU_IMAGE,
    )


@app.route("/owner/restaurant/update", methods=["POST"])
def update_owner_restaurant_info():
    current_user, response = get_owner_user_or_redirect()

    if response:
        return response

    restaurant, response = get_selected_owner_restaurant(current_user)

    if response:
        return response

    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    address = request.form.get("address", "").strip()

    if not name or not category or not address:
        flash("Please complete restaurant name, category, and address.", "danger")
        return redirect_back_to_owner(restaurant.id)

    restaurant.name = name
    restaurant.category = category
    restaurant.address = address
    restaurant.suburb = request.form.get("suburb", "").strip() or None
    restaurant.phone = request.form.get("phone", "").strip() or None
    restaurant.website = request.form.get("website", "").strip() or None
    restaurant.description = request.form.get("description", "").strip() or None
    restaurant.updated_at = datetime.utcnow()

    db.session.commit()
    flash("Restaurant information updated.", "success")

    return redirect_back_to_owner(restaurant.id)


@app.route("/owner/opening-hours/update", methods=["POST"])
def update_owner_opening_hours():
    current_user, response = get_owner_user_or_redirect()

    if response:
        return response

    restaurant, response = get_selected_owner_restaurant(current_user)

    if response:
        return response

    for hour in restaurant.opening_hours:
        is_closed = request.form.get(f"is_closed_{hour.id}") == "on"
        hour.is_closed = is_closed

        if is_closed:
            hour.open_time = None
            hour.close_time = None
        else:
            hour.open_time = (
                request.form.get(f"open_time_{hour.id}", "").strip() or None
            )
            hour.close_time = (
                request.form.get(f"close_time_{hour.id}", "").strip() or None
            )

    restaurant.updated_at = datetime.utcnow()
    db.session.commit()

    flash("Opening hours updated.", "success")
    return redirect_back_to_owner(restaurant.id)


@app.route("/owner/menu-items/add", methods=["POST"])
def add_owner_menu_item():
    current_user, response = get_owner_user_or_redirect()

    if response:
        return response

    restaurant, response = get_selected_owner_restaurant(current_user)

    if response:
        return response

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    price_text = request.form.get("price", "").strip()
    uploaded_image_url = save_menu_image(request.files.get("image_file"))

    if uploaded_image_url is None:
        return redirect_back_to_owner(restaurant.id)

    if not name:
        flash("Please enter a menu item name.", "danger")
        return redirect_back_to_owner(restaurant.id)

    try:
        price = float(price_text) if price_text else None
    except ValueError:
        flash("Please enter a valid menu item price.", "danger")
        return redirect_back_to_owner(restaurant.id)

    menu_item = MenuItem(
        restaurant_id=restaurant.id,
        name=name,
        description=description or None,
        price=price,
        image_url=uploaded_image_url or None,
    )

    db.session.add(menu_item)
    restaurant.updated_at = datetime.utcnow()
    db.session.commit()

    flash("Menu item added.", "success")
    return redirect_back_to_owner(restaurant.id)


@app.route("/owner/menu-items/<int:menu_item_id>/update", methods=["POST"])
def update_owner_menu_item(menu_item_id):
    current_user, response = get_owner_user_or_redirect()

    if response:
        return response

    restaurant, response = get_selected_owner_restaurant(current_user)

    if response:
        return response

    menu_item = MenuItem.query.filter_by(
        id=menu_item_id,
        restaurant_id=restaurant.id,
    ).first_or_404()

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    price_text = request.form.get("price", "").strip()
    uploaded_image_url = save_menu_image(request.files.get("image_file"))

    if uploaded_image_url is None:
        return redirect_back_to_owner(restaurant.id)

    if not name:
        flash("Please enter a menu item name.", "danger")
        return redirect_back_to_owner(restaurant.id)

    try:
        price = float(price_text) if price_text else None
    except ValueError:
        flash("Please enter a valid menu item price.", "danger")
        return redirect_back_to_owner(restaurant.id)

    menu_item.name = name
    menu_item.description = description or None
    menu_item.price = price

    # update only if new file
    if uploaded_image_url:
        menu_item.image_url = uploaded_image_url

    restaurant.updated_at = datetime.utcnow()

    db.session.commit()

    flash("Menu item updated.", "success")
    return redirect_back_to_owner(restaurant.id)


@app.route("/owner/menu-items/<int:menu_item_id>/delete", methods=["POST"])
def delete_owner_menu_item(menu_item_id):
    current_user, response = get_owner_user_or_redirect()

    if response:
        return response

    restaurant, response = get_selected_owner_restaurant(current_user)

    if response:
        return response

    menu_item = MenuItem.query.filter_by(
        id=menu_item_id,
        restaurant_id=restaurant.id,
    ).first_or_404()

    db.session.delete(menu_item)
    restaurant.updated_at = datetime.utcnow()
    db.session.commit()

    flash("Menu item deleted.", "success")
    return redirect_back_to_owner(restaurant.id)


@app.route("/owner/reviews/<int:review_id>/report", methods=["POST"])
def report_owner_review(review_id):
    current_user, response = get_owner_user_or_redirect()

    if response:
        return response

    restaurant, response = get_selected_owner_restaurant(current_user)

    if response:
        return response

    review = Review.query.filter_by(
        id=review_id,
        restaurant_id=restaurant.id,
    ).first_or_404()

    review.status = "reported"
    review.updated_at = datetime.utcnow()
    db.session.commit()

    flash("Review reported to admin.", "success")
    return redirect_back_to_owner(restaurant.id)


@app.route("/owner/reviews/<int:review_id>/cancel-report", methods=["POST"])
def cancel_owner_review_report(review_id):
    current_user, response = get_owner_user_or_redirect()

    if response:
        return response

    restaurant, response = get_selected_owner_restaurant(current_user)

    if response:
        return response

    review = Review.query.filter_by(
        id=review_id,
        restaurant_id=restaurant.id,
    ).first_or_404()

    review.status = "active"
    review.updated_at = datetime.utcnow()
    db.session.commit()

    flash("Review report cancelled.", "success")
    return redirect_back_to_owner(restaurant.id)
