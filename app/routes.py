from flask import render_template, redirect, url_for
from app import app


@app.route("/")
def home():
    return redirect(url_for("restaurant_detail", restaurant_id=1))


@app.route("/restaurants/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    restaurant = {
        "id": restaurant_id,
        "name": "Laneway Pizza Co.",
        "category": "Italian",
        "rating": 4.7,
        "review_count": 512,
        "address": "Barrack St, Perth WA 6000",
        "phone": "+61 8 1234 5678",
        "website": "https://example.com",
    }

    return render_template(
        "restaurant_detail.html",
        restaurant=restaurant,
    )