from flask import flash, redirect, render_template, request, session, url_for
from app import app, db
from app.utils import make_star_text
from app.models import Restaurant, MenuItem, OpeningHour, Review, User
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime
from urllib.parse import quote_plus

DEFAULT_PROFILE_IMAGE = "https://ui-avatars.com/api/?name=TableTrail&background=dcfce7&color=15803d&bold=true"
DEFAULT_RESTAURANT_IMAGE = "images/restaurant-default.png"
DEFAULT_MENU_IMAGE = "images/menu-default.png"
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
SEARCH_MAP_LOCATION_COLORS = [
    "#15803d",
    "#2563eb",
    "#dc2626",
    "#9333ea",
    "#ea580c",
    "#0891b2",
    "#be123c",
    "#4f46e5",
    "#65a30d",
    "#c2410c",
]


def build_openstreetmap_url(restaurants):
    if not restaurants:
        return "https://www.openstreetmap.org/#map=12/-31.9523/115.8613"

    coordinates = SEARCH_MAP_COORDINATES.get(restaurants[0].suburb or "")

    if not coordinates:
        coordinates = {"lat": -31.9523, "lng": 115.8613}

    query = quote_plus(f"{restaurants[0].name}, {restaurants[0].address}, Australia")
    return (
        "https://www.openstreetmap.org/search"
        f"?query={query}"
        f"#map=14/{coordinates['lat']}/{coordinates['lng']}"
    )


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


def build_search_map_markers(restaurants):
    markers = []
    location_colors = {}

    for index, restaurant in enumerate(restaurants):
        location_key = restaurant.suburb or "Other"
        coordinates = SEARCH_MAP_COORDINATES.get(location_key)

        if not coordinates:
            coordinates = {
                "lat": -31.9523 + (((restaurant.id * 17) % 40) - 20) / 1000,
                "lng": 115.8613 + (((restaurant.id * 29) % 40) - 20) / 1000,
            }

        if location_key not in location_colors:
            color_index = len(location_colors) % len(SEARCH_MAP_LOCATION_COLORS)
            location_colors[location_key] = SEARCH_MAP_LOCATION_COLORS[color_index]

        markers.append(
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "category": restaurant.category,
                "address": restaurant.address,
                "suburb": restaurant.suburb,
                "location_color": location_colors[location_key],
                "rating": round(restaurant.average_rating or 0, 1),
                "review_count": restaurant.review_count,
                "marker_number": index + 1,
                "latitude": coordinates["lat"],
                "longitude": coordinates["lng"],
                "detail_url": url_for("restaurant_detail", restaurant_id=restaurant.id),
            }
        )

    return markers


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
        flash(
            "If an account exists for that email, reset instructions will be sent.",
            "success",
        )

    return render_template("forgot_password.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "customer")
        abn_number = request.form.get("abn_number", "").strip()
        contact_number = request.form.get("contact_number", "").strip()

        if not username or not email or not password:
            flash("Please complete all required fields.", "danger")
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
        profile_image = request.form.get("profile_image", "").strip()

        if not username or not email:
            flash("Please enter your username and email.", "danger")
            return redirect(url_for("profile"))

        existing_user = User.query.filter(
            User.email == email, User.id != user.id
        ).first()

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
        Review.query.filter_by(user_id=user.id).order_by(Review.created_at.desc()).all()
    )

    return render_template(
        "profile.html",
        user=user,
        initials=make_initials(user.username),
        profile_image=user.profile_image,
        reviews=reviews,
    )


@app.route("/search")
def search():
    keyword = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    category = request.args.get("category", "").strip()
    filter_location = request.args.get("filter_location", "").strip()
    rating = request.args.get("rating", "").strip()
    sort = request.args.get("sort", "rating").strip()
    active_location = filter_location or location

    query = Restaurant.query

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

    if active_location:
        search_map_label = active_location
    elif restaurants:
        search_map_label = restaurants[0].suburb or restaurants[0].address
    else:
        search_map_label = "Perth"

    search_map_markers = build_search_map_markers(restaurants)
    search_map_search_url = build_openstreetmap_url(restaurants)

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

    return render_template(
        "search.html",
        restaurants=restaurants,
        categories=categories,
        locations=locations,
        default_restaurant_image=DEFAULT_RESTAURANT_IMAGE,
        search_map_markers=search_map_markers,
        search_map_search_url=search_map_search_url,
        search_map_label=search_map_label,
        search_summary_label=search_summary_label,
    )


@app.route("/bookmarks")
def bookmarks():
    saved_restaurants = [
        {
            "id": 5,
            "name": "Green Bowl Kitchen",
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
            "id": 1,
            "name": "Laneway Pizza Co.",
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
            "id": 2,
            "name": "Northbridge Coffee Lab",
            "category": "Cafe",
            "location": "Northbridge",
            "price": "$$",
            "rating": 4.5,
            "star_text": make_star_text(4.5),
            "review_count": 2,
            "description": "Specialty coffee and brunch near Northbridge.",
            "image": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1200&q=80",
        },
    ]

    bookmark_collections = [
        {
            "id": "weekend-brunch",
            "name": "Weekend brunch",
            "visibility": "Public",
            "share_code": "BRUNCH-4827",
            "cover_image": saved_restaurants[0]["image"],
            "restaurant_count": 2,
            "description": "Easy cafes and light meals for slow weekend mornings.",
            "restaurants": [saved_restaurants[0], saved_restaurants[2]],
        },
        {
            "id": "dinner-shortlist",
            "name": "Dinner shortlist",
            "visibility": "Private",
            "share_code": "DINNER-9135",
            "cover_image": saved_restaurants[1]["image"],
            "restaurant_count": 2,
            "description": "Places worth trying for relaxed dinners with friends.",
            "restaurants": [saved_restaurants[1], saved_restaurants[0]],
        },
        {
            "id": "city-lunch",
            "name": "City lunch ideas",
            "visibility": "Public",
            "share_code": "LUNCH-2058",
            "cover_image": saved_restaurants[2]["image"],
            "restaurant_count": 2,
            "description": "Fast, reliable restaurants around Perth CBD.",
            "restaurants": [saved_restaurants[2], saved_restaurants[1]],
        },
    ]

    return render_template(
        "bookmarks.html",
        saved_restaurants=saved_restaurants,
        bookmark_collections=bookmark_collections,
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
        {
            "day": "Monday",
            "open_time": "07:00",
            "close_time": "23:00",
            "is_closed": False,
        },
        {
            "day": "Tuesday",
            "open_time": "07:00",
            "close_time": "23:00",
            "is_closed": False,
        },
        {
            "day": "Wednesday",
            "open_time": "07:00",
            "close_time": "23:00",
            "is_closed": False,
        },
        {
            "day": "Thursday",
            "open_time": "07:00",
            "close_time": "23:00",
            "is_closed": False,
        },
        {
            "day": "Friday",
            "open_time": "07:00",
            "close_time": "00:00",
            "is_closed": False,
        },
        {
            "day": "Saturday",
            "open_time": "08:00",
            "close_time": "00:00",
            "is_closed": False,
        },
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
