from flask import render_template, redirect, url_for
from app import app
from app.utils import make_star_text
from app.models import Restaurant, MenuItem, OpeningHour, Review

from datetime import datetime


@app.route("/")
def home():
    return redirect(url_for("restaurant_detail", restaurant_id=1))


@app.route("/restaurants/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    # restaurant summary
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    star_text = make_star_text(restaurant.average_rating)

    # restaurant opening hours
    opening_hours = (
        OpeningHour.query.filter_by(restaurant_id=restaurant.id)
        .order_by(OpeningHour.day_of_week)
        .all()
    )

    today_day_of_week = datetime.today().weekday()

    # restaurant menu highlights
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).all()

    review_summary = {
        "distribution": [
            {"stars": 5, "count": 390, "percentage": 76},
            {"stars": 4, "count": 82, "percentage": 16},
            {"stars": 3, "count": 26, "percentage": 5},
            {"stars": 2, "count": 9, "percentage": 2},
            {"stars": 1, "count": 5, "percentage": 1},
        ],
    }

    reviews = (
        Review.query.filter_by(restaurant_id=restaurant.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return render_template(
        "restaurant_detail.html",
        restaurant=restaurant,
        opening_hours=opening_hours,
        menu_items=menu_items,
        review_summary=review_summary,
        reviews=reviews,
        star_text=star_text,
        today_day_of_week=today_day_of_week,
        is_logged_in=True,
    )


@app.route("/restaurants/<int:restaurant_id>/menu")
def restaurant_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    return render_template("restaurant_menu.html", restaurant=restaurant)
