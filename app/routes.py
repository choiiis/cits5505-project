from flask import flash, redirect, render_template, request, session, url_for
from app import app
from app.utils import make_star_text
from app.models import Restaurant, MenuItem, OpeningHour, Review, User
from werkzeug.security import check_password_hash

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


@app.route("/")
def home():
    return redirect(url_for("restaurant_detail", restaurant_id=1))


@app.route("/home-test")
def home_test():
    return render_template("home.html")


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


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


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
    return render_template("admin_dashboard.html")


@app.route("/owner")
def owner_dashboard():
    return render_template("owner_dashboard.html")
