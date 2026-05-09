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
    return render_template("index.html")

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
