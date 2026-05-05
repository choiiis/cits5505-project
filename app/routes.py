from flask import render_template, redirect, url_for
from app import app
from app.utils import make_star_text
from app.models import Restaurant, MenuItem, OpeningHour

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

    reviews = [
        {
            "username": "Alex",
            "rating": 5,
            "date": "03 Apr 2026",
            "review_count": 12,
            "content": "Great pizza and a nice late-night atmosphere. The crust was perfectly crispy and the staff were really friendly.",
            "profile_image": "https://randomuser.me/api/portraits/men/32.jpg",
            "photos": [
                "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=800&q=80",
            ],
            "is_author": True,
        },
        {
            "username": "Mia",
            "rating": 4,
            "date": "31 Mar 2026",
            "review_count": 8,
            "content": "Good food overall and the dessert was definitely the highlight. It gets a little busy on weekends, but still worth visiting.",
            "profile_image": "https://randomuser.me/api/portraits/women/44.jpg",
            "photos": [],
            "is_author": False,
        },
        {
            "username": "Daniel",
            "rating": 5,
            "date": "28 Mar 2026",
            "review_count": 15,
            "content": "Loved the truffle mushroom pizza and tiramisu. Cozy atmosphere and quick service made it a great place for dinner with friends.",
            "profile_image": "https://randomuser.me/api/portraits/men/75.jpg",
            "photos": [],
            "is_author": False,
        },
    ]

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
