from app import app, db
from app.models import (
    User,
    Restaurant,
    MenuItem,
    OpeningHour,
    Review,
    ReviewPhoto,
    BookmarkCollection,
    Bookmark,
)


def clear_data():
    ReviewPhoto.query.delete()
    Review.query.delete()
    Bookmark.query.delete()
    BookmarkCollection.query.delete()
    OpeningHour.query.delete()
    MenuItem.query.delete()
    Restaurant.query.delete()
    User.query.delete()
    db.session.commit()


def create_opening_hours(
    restaurant_id,
    weekday_hours,
    friday_hours=None,
    weekend_hours=None,
    closed_days=None,
):
    """Create a simple 7-day opening hour schedule for a restaurant."""
    friday_hours = friday_hours or weekday_hours
    weekend_hours = weekend_hours or weekday_hours
    closed_days = closed_days or []

    days = [
        (0, "Mon", weekday_hours[0], weekday_hours[1]),
        (1, "Tue", weekday_hours[0], weekday_hours[1]),
        (2, "Wed", weekday_hours[0], weekday_hours[1]),
        (3, "Thu", weekday_hours[0], weekday_hours[1]),
        (4, "Fri", friday_hours[0], friday_hours[1]),
        (5, "Sat", weekend_hours[0], weekend_hours[1]),
        (6, "Sun", weekend_hours[0], weekend_hours[1]),
    ]

    return [
        OpeningHour(
            restaurant_id=restaurant_id,
            day_of_week=day_of_week,
            day_label=day_label,
            open_time=None if day_of_week in closed_days else open_time,
            close_time=None if day_of_week in closed_days else close_time,
            is_closed=day_of_week in closed_days,
        )
        for day_of_week, day_label, open_time, close_time in days
    ]


def seed_data():
    # Users
    alex = User(
        email="alex@example.com",
        username="Alex",
        password_hash="dev-password-hash",
        role="customer",
    )

    mia = User(
        email="mia@example.com",
        username="Mia",
        password_hash="dev-password-hash",
        role="customer",
    )

    daniel = User(
        email="daniel@example.com",
        username="Daniel",
        password_hash="dev-password-hash",
        role="customer",
    )

    owner = User(
        email="owner@example.com",
        username="Restaurant Owner",
        password_hash="dev-password-hash",
        role="owner",
        abn_number="51824753556",
        contact_number="+61 8 1234 5678",
    )

    db.session.add_all([alex, mia, daniel, owner])
    db.session.commit()

    # Restaurants
    laneway_pizza = Restaurant(
        name="Laneway Pizza Co.",
        category="Italian",
        description="A casual pizza spot in Perth CBD.",
        address="Barrack St, Perth, WA 6000",
        suburb="Perth CBD",
        phone="+61 8 1234 5678",
        website="https://example.com",
        thumbnail_image="images/margherita.jpg",
        hero_image="https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1200&q=80",
        average_rating=4.7,
        review_count=3,
        owner_id=owner.id,
    )

    northbridge_cafe = Restaurant(
        name="Northbridge Coffee Lab",
        category="Cafe",
        description="Specialty coffee and brunch near Northbridge.",
        address="William St, Northbridge, WA 6003",
        suburb="Northbridge",
        phone="+61 8 2222 3333",
        website="https://example.com",
        thumbnail_image="images/margherita.jpg",
        hero_image="https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1200&q=80",
        average_rating=4.5,
        review_count=2,
    )

    seoul_table = Restaurant(
        name="Seoul Table",
        category="Korean",
        description="Korean comfort food and BBQ in Victoria Park.",
        address="Albany Hwy, Victoria Park, WA 6100",
        suburb="Victoria Park",
        phone="+61 8 4444 5555",
        website="https://example.com",
        thumbnail_image="images/margherita.jpg",
        hero_image="https://images.unsplash.com/photo-1498654896293-37aacf113fd9?auto=format&fit=crop&w=1200&q=80",
        average_rating=4.8,
        review_count=4,
    )

    burger_corner = Restaurant(
        name="Burger Corner",
        category="Fast Food",
        description="Quick burgers, fries, and late-night comfort food.",
        address="Murray St, Perth, WA 6000",
        suburb="Perth CBD",
        phone="+61 8 7777 8888",
        website="https://example.com",
        thumbnail_image="images/margherita.jpg",
        hero_image="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=1200&q=80",
        average_rating=4.2,
        review_count=6,
    )

    green_bowl = Restaurant(
        name="Green Bowl Kitchen",
        category="Healthy",
        description="Fresh bowls, salads, smoothies, and vegan-friendly meals.",
        address="Hay St, Subiaco, WA 6008",
        suburb="Subiaco",
        phone="+61 8 9999 1111",
        website="https://example.com",
        thumbnail_image="images/margherita.jpg",
        hero_image="https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1200&q=80",
        average_rating=4.4,
        review_count=3,
    )

    db.session.add_all(
        [
            laneway_pizza,
            northbridge_cafe,
            seoul_table,
            burger_corner,
            green_bowl,
        ]
    )
    db.session.commit()

    # Menu items
    menu_items = [
        MenuItem(
            restaurant_id=laneway_pizza.id,
            name="Margherita Pizza",
            description="Tomato, mozzarella, basil",
            price=22.0,
            image_url="images/margherita.jpg",
        ),
        MenuItem(
            restaurant_id=laneway_pizza.id,
            name="Truffle Mushroom Pizza",
            description="Mushroom, truffle oil, mozzarella",
            price=27.0,
            image_url="images/margherita.jpg",
        ),
        MenuItem(
            restaurant_id=laneway_pizza.id,
            name="Tiramisu",
            description="Coffee, mascarpone, cocoa",
            price=14.0,
            image_url="images/margherita.jpg",
        ),
        MenuItem(
            restaurant_id=northbridge_cafe.id,
            name="Iced Latte",
            description="Espresso, milk, ice",
            price=6.5,
            image_url="images/margherita.jpg",
        ),
        MenuItem(
            restaurant_id=northbridge_cafe.id,
            name="Avocado Toast",
            description="Sourdough, avocado, feta, chilli flakes",
            price=18.0,
            image_url="images/margherita.jpg",
        ),
        MenuItem(
            restaurant_id=seoul_table.id,
            name="Bibimbap",
            description="Rice bowl with vegetables, beef, egg, and gochujang",
            price=21.0,
            image_url="images/margherita.jpg",
        ),
        MenuItem(
            restaurant_id=seoul_table.id,
            name="Kimchi Stew",
            description="Spicy kimchi stew with pork and tofu",
            price=19.0,
            image_url="images/margherita.jpg",
        ),
        MenuItem(
            restaurant_id=burger_corner.id,
            name="Classic Cheeseburger",
            description="Beef patty, cheddar, pickles, lettuce, house sauce",
            price=16.0,
            image_url="images/margherita.jpg",
        ),
        MenuItem(
            restaurant_id=green_bowl.id,
            name="Salmon Poke Bowl",
            description="Rice, salmon, edamame, cucumber, avocado",
            price=23.0,
            image_url="images/margherita.jpg",
        ),
    ]

    db.session.add_all(menu_items)

    # Opening hours
    # Keep one restaurant without opening hours to test the fallback UI.
    db.session.add_all(
        create_opening_hours(
            laneway_pizza.id,
            weekday_hours=("7:00 AM", "11:00 PM"),
            friday_hours=("7:00 AM", "12:00 AM"),
            weekend_hours=("8:00 AM", "12:00 AM"),
            closed_days=[1],  # Tuesday closed
        )
    )

    db.session.add_all(
        create_opening_hours(
            northbridge_cafe.id,
            weekday_hours=("6:30 AM", "3:00 PM"),
            weekend_hours=("7:00 AM", "2:00 PM"),
            closed_days=[6],  # Sunday closed
        )
    )

    db.session.add_all(
        create_opening_hours(
            seoul_table.id,
            weekday_hours=("11:30 AM", "9:30 PM"),
            friday_hours=("11:30 AM", "10:30 PM"),
            weekend_hours=("11:30 AM", "10:30 PM"),
            closed_days=[0],  # Monday closed
        )
    )

    db.session.add_all(
        create_opening_hours(
            burger_corner.id,
            weekday_hours=("10:00 AM", "10:00 PM"),
            friday_hours=("10:00 AM", "1:00 AM"),
            weekend_hours=("11:00 AM", "1:00 AM"),
        )
    )

    # green_bowl intentionally has no opening hours.

    db.session.commit()

    # Reviews
    reviews = [
        Review(
            restaurant_id=laneway_pizza.id,
            user_id=alex.id,
            rating=5,
            content="Great pizza and a nice late-night atmosphere. The crust was perfectly crispy and the staff were friendly.",
        ),
        Review(
            restaurant_id=laneway_pizza.id,
            user_id=mia.id,
            rating=4,
            content="Good food overall and the dessert was definitely the highlight.",
        ),
        Review(
            restaurant_id=laneway_pizza.id,
            user_id=daniel.id,
            rating=5,
            content="Loved the truffle mushroom pizza and tiramisu. Cozy atmosphere and quick service.",
        ),
        Review(
            restaurant_id=northbridge_cafe.id,
            user_id=alex.id,
            rating=5,
            content="Excellent coffee and a calm place to study in the morning.",
        ),
        Review(
            restaurant_id=northbridge_cafe.id,
            user_id=mia.id,
            rating=4,
            content="Nice brunch menu and friendly service.",
        ),
        Review(
            restaurant_id=seoul_table.id,
            user_id=daniel.id,
            rating=5,
            content="The kimchi stew was rich and comforting. Great place for dinner.",
        ),
        Review(
            restaurant_id=burger_corner.id,
            user_id=alex.id,
            rating=4,
            content="Good late-night burger option in the city.",
        ),
        Review(
            restaurant_id=green_bowl.id,
            user_id=mia.id,
            rating=4,
            content="Fresh bowls and good vegan options.",
        ),
    ]

    db.session.add_all(reviews)
    db.session.commit()

    review_photos = [
        ReviewPhoto(
            review_id=reviews[0].id,
            image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
        ),
        ReviewPhoto(
            review_id=reviews[0].id,
            image_url="https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=800&q=80",
        ),
        ReviewPhoto(
            review_id=reviews[5].id,
            image_url="https://images.unsplash.com/photo-1498654896293-37aacf113fd9?auto=format&fit=crop&w=800&q=80",
        ),
    ]

    db.session.add_all(review_photos)

    # Bookmark collections
    perth_best = BookmarkCollection(
        user_id=alex.id,
        name="Perth best",
        description="My favourite restaurants around Perth.",
        is_public=True,
    )

    study_cafes = BookmarkCollection(
        user_id=alex.id,
        name="Study cafes",
        description="Places with coffee and a good study atmosphere.",
        is_public=False,
    )

    dinner_shortlist = BookmarkCollection(
        user_id=mia.id,
        name="Dinner shortlist",
        description="Restaurants to try for dinner.",
        is_public=True,
    )

    db.session.add_all([perth_best, study_cafes, dinner_shortlist])
    db.session.commit()

    bookmarks = [
        Bookmark(collection_id=perth_best.id, restaurant_id=laneway_pizza.id),
        Bookmark(collection_id=perth_best.id, restaurant_id=seoul_table.id),
        Bookmark(collection_id=perth_best.id, restaurant_id=northbridge_cafe.id),
        Bookmark(collection_id=study_cafes.id, restaurant_id=northbridge_cafe.id),
        Bookmark(collection_id=study_cafes.id, restaurant_id=green_bowl.id),
        Bookmark(collection_id=dinner_shortlist.id, restaurant_id=laneway_pizza.id),
        Bookmark(collection_id=dinner_shortlist.id, restaurant_id=burger_corner.id),
    ]

    db.session.add_all(bookmarks)
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        clear_data()
        seed_data()
        print("Database seeded successfully.")
