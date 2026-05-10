from flask import flash, redirect, render_template, request, session, url_for
from app import app, db
from app.utils import make_star_text
from app.models import Restaurant, MenuItem, OpeningHour, Review, User
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime


def is_valid_login(user, password):
    if not user or not password:
        return False

    if user.password_hash == "dev-password-hash":
        return password == "password"

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


def make_initials(username):
    parts = username.split()
    if not parts:
        return "TT"

    return "".join(part[0] for part in parts[:2]).upper()


def build_home_context():
    home_categories = ["Italian", "Japanese", "Cafe", "Thai", "Dessert"]
    featured_restaurants = [
        {
            "name": "Green Bowl Kitchen",
            "restaurant_id": 5,
            "category": "Healthy",
            "location": "Subiaco",
            "price": "$$",
            "rating": 4.4,
            "star_text": make_star_text(4.4),
            "review_count": 3,
            "description": "Fresh bowls, salads, smoothies, and vegan-friendly meals.",
            "image": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1200&q=80",
        },
        {
            "name": "Laneway Pizza Co.",
            "restaurant_id": 1,
            "category": "Italian",
            "location": "Perth CBD",
            "price": "$$",
            "rating": 4.7,
            "star_text": make_star_text(4.7),
            "review_count": 3,
            "description": "A casual pizza spot in Perth CBD.",
            "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1200&q=80",
        },
        {
            "name": "Northbridge Coffee Lab",
            "restaurant_id": 2,
            "category": "Cafe",
            "location": "Northbridge",
            "price": "$$",
            "rating": 4.5,
            "star_text": make_star_text(4.5),
            "review_count": 2,
            "description": "Specialty coffee and brunch near Northbridge.",
            "image": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1200&q=80",
        },
        {
            "name": "Seoul Table",
            "restaurant_id": 3,
            "category": "Korean",
            "location": "Victoria Park",
            "price": "$$",
            "rating": 4.8,
            "star_text": make_star_text(4.8),
            "review_count": 4,
            "description": "Korean comfort food and BBQ in Victoria Park.",
            "image": "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?auto=format&fit=crop&w=1200&q=80",
        },
    ]

    return {
        "home_categories": home_categories,
        "featured_restaurants": featured_restaurants,
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
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if is_valid_login(user, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Welcome back, {user.username}.", "success")
            return redirect(url_for("restaurant_detail", restaurant_id=1))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Please enter your email address.", "danger")
            return render_template("forgot_password.html")

        User.query.filter_by(email=email).first()
        flash("If an account exists for that email, reset instructions will be sent.", "success")

    return render_template("forgot_password.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("Please complete all required fields.", "danger")
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
            role="customer",
        )

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        session["username"] = user.username
        flash(f"Welcome to TableTrail, {user.username}.", "success")
        return redirect(url_for("restaurant_detail", restaurant_id=1))

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
        email = request.form.get("email", "").strip().lower()
        profile_image = request.form.get("profileImage", "").strip()

        if not username or not email:
            flash("Please enter your username and email.", "danger")
            return redirect(url_for("profile"))

        existing_user = User.query.filter(User.email == email, User.id != user.id).first()

        if existing_user:
            flash("That email is already used by another account.", "danger")
            return redirect(url_for("profile"))

        user.username = username
        user.email = email
        user.profile_image = profile_image or None
        db.session.commit()

        session["username"] = user.username
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    reviews = (
        Review.query.filter_by(user_id=user.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return render_template(
        "profile.html",
        user=user,
        initials=make_initials(user.username),
        reviews=reviews,
    )


@app.route("/search")
def search():
    restaurants = [
        {
            "id": 1,
            "name": "Little Italy",
            "category": "Italian",
            "location": "Northbridge",
            "rating": 4.6,
            "review_count": 128,
            "description": "Authentic Italian cuisine in the heart of Northbridge. Fresh pasta, wood-fired pizza, and a great wine list.",
            "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80",
            "tags": ["$$", "Vegetarian options", "Outdoor seating"],
        },
        {
            "id": 2,
            "name": "Sakura Sushi",
            "category": "Japanese",
            "location": "Subiaco",
            "rating": 4.4,
            "review_count": 96,
            "description": "Fresh and authentic Japanese cuisine. Sushi, sashimi and more.",
            "image_url": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=1200&q=80",
            "tags": ["$$", "Gluten-free options", "Takeaway"],
        },
        {
            "id": 3,
            "name": "Greenhouse Cafe",
            "category": "Cafe",
            "location": "Fremantle",
            "rating": 4.3,
            "review_count": 72,
            "description": "Relaxed cafe with excellent coffee, brunch, and house-made pastries.",
            "image_url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1200&q=80",
            "tags": ["$", "Vegan options", "Outdoor seating"],
        },
    ]

    categories = ["Italian", "Japanese", "Mexican", "Cafe"]
    locations = ["Northbridge", "Fremantle", "Subiaco", "Perth CBD"]

    return render_template(
        "search.html",
        restaurants=restaurants,
        categories=categories,
        locations=locations,
    )


@app.route("/restaurants/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    # restaurant summary
    restaurant = Restaurant.query.get_or_404(restaurant_id)

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
        Review.query.filter_by(restaurant_id=restaurant.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    review_summary = build_review_summary(reviews)
    star_text = make_star_text(review_summary["average_rating"])

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
    )


@app.route("/restaurants/<int:restaurant_id>/menu")
def restaurant_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    return render_template("restaurant_menu.html", restaurant=restaurant)


@app.route("/admin")
def admin_dashboard():
    admin_stats = [
        {"label": "Total Users", "value": "1,248"},
        {"label": "Total Restaurants", "value": "86"},
        {"label": "Pending Approval", "value": "7"},
        {"label": "Reported Listings", "value": "3"},
    ]

    restaurants = [
        {
            "name": "Laneway Pizza Co.",
            "category": "Italian",
            "owner": "Mia Chen",
            "status": "Approved",
            "status_class": "admin-status--approved",
            "rating": "4.7",
            "action": "View",
        },
        {
            "name": "Ocean View Cafe",
            "category": "Modern Australian",
            "owner": "David Lee",
            "status": "Pending",
            "status_class": "admin-status--pending",
            "rating": "4.3",
            "action": "Review",
        },
        {
            "name": "Green Garden Bistro",
            "category": "Vegetarian",
            "owner": "Sarah Green",
            "status": "Reported",
            "status_class": "admin-status--reported",
            "rating": "3.9",
            "action": "Check",
        },
    ]

    users = [
        {
            "name": "Alex Wong",
            "email": "alex@example.com",
            "role": "Customer",
            "status": "Active",
            "status_class": "admin-status--approved",
            "action": "View",
        },
        {
            "name": "Mia Chen",
            "email": "mia@example.com",
            "role": "Owner",
            "status": "Active",
            "status_class": "admin-status--approved",
            "action": "View",
        },
        {
            "name": "Jordan Smith",
            "email": "jordan@example.com",
            "role": "Customer",
            "status": "Under Review",
            "status_class": "admin-status--pending",
            "action": "Check",
        },
    ]

    admin_tasks = [
        {
            "title": "Approve restaurants",
            "description": "Review new restaurant submissions and approve listings that meet the platform requirements.",
        },
        {
            "title": "Manage reports",
            "description": "Check reported restaurants, reviews, or users and decide whether action is needed.",
        },
        {
            "title": "Monitor users",
            "description": "View user roles, account status, and activity before connecting full admin controls.",
        },
    ]

    return render_template(
        "admin_dashboard.html",
        admin_stats=admin_stats,
        restaurants=restaurants,
        users=users,
        admin_tasks=admin_tasks,
    )
    
@app.route("/owner")
def owner_dashboard():
    restaurant = {
        "id": 1,
        "name": "Laneway Pizza Co.",
        "category": "Italian",
        "address": "Barrack St, Perth, WA 6000",
        "phone": "+61 8 1234 5678",
        "website": "https://example.com",
        "status": "Approved",
        "rating": "4.7",
        "review_count": "512",
    }

    owner_stats = [
        {"label": "Restaurant", "value": restaurant["name"]},
        {"label": "Listing Status", "value": restaurant["status"]},
        {"label": "Rating", "value": restaurant["rating"]},
        {"label": "Reviews", "value": restaurant["review_count"]},
    ]

    restaurant_info = [
        {"label": "Restaurant Name", "field": "name", "value": restaurant["name"]},
        {"label": "Category", "field": "category", "value": restaurant["category"]},
        {"label": "Address", "field": "address", "value": restaurant["address"]},
        {"label": "Phone", "field": "phone", "value": restaurant["phone"]},
        {"label": "Website", "field": "website", "value": restaurant["website"]},
    ]

    opening_hours = [
        {"day": "Monday", "open_time": "07:00", "close_time": "23:00", "is_closed": False},
        {"day": "Tuesday", "open_time": "07:00", "close_time": "23:00", "is_closed": False},
        {"day": "Wednesday", "open_time": "07:00", "close_time": "23:00", "is_closed": False},
        {"day": "Thursday", "open_time": "07:00", "close_time": "23:00", "is_closed": False},
        {"day": "Friday", "open_time": "07:00", "close_time": "00:00", "is_closed": False},
        {"day": "Saturday", "open_time": "08:00", "close_time": "00:00", "is_closed": False},
        {"day": "Sunday", "open_time": "", "close_time": "", "is_closed": True},
    ]

    menu_items = [
        {
            "name": "Margherita Pizza",
            "category": "Pizza",
            "price": "$22",
            "status": "Available",
            "status_class": "owner-status--available",
        },
        {
            "name": "Truffle Mushroom Pizza",
            "category": "Pizza",
            "price": "$27",
            "status": "Available",
            "status_class": "owner-status--available",
        },
        {
            "name": "Tiramisu",
            "category": "Dessert",
            "price": "$14",
            "status": "Hidden",
            "status_class": "owner-status--hidden",
        },
    ]

    owner_tasks = [
        {
            "title": "Edit restaurant profile",
            "description": "Update restaurant name, category, contact details, website, images, and description.",
        },
        {
            "title": "Manage opening hours",
            "description": "Change daily opening times and mark specific days as closed.",
        },
        {
            "title": "Review listing status",
            "description": "Check whether the restaurant listing is approved, pending, hidden, or reported.",
        },
    ]

    return render_template(
        "owner_dashboard.html",
        restaurant=restaurant,
        owner_stats=owner_stats,
        restaurant_info=restaurant_info,
        opening_hours=opening_hours,
        menu_items=menu_items,
        owner_tasks=owner_tasks,
    )