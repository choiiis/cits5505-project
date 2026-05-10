from datetime import datetime
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_image = db.Column(db.String(255))

    role = db.Column(db.String(20), nullable=False, default="customer")
    restaurant_name = db.Column(db.String(120))
    abn_number = db.Column(db.String(20))
    contact_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    reviews = db.relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )

    owned_restaurants = db.relationship("Restaurant", back_populates="owner")

    bookmark_collections = db.relationship(
        "BookmarkCollection", back_populates="user", cascade="all, delete-orphan"
    )


class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    description = db.Column(db.Text)

    address = db.Column(db.String(255), nullable=False)
    suburb = db.Column(db.String(80), index=True)

    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))

    thumbnail_image = db.Column(db.String(255))
    hero_image = db.Column(db.String(500))

    average_rating = db.Column(db.Float, nullable=False, default=0.0)
    review_count = db.Column(db.Integer, nullable=False, default=0)

    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    owner = db.relationship("User", back_populates="owned_restaurants")

    menu_items = db.relationship(
        "MenuItem", back_populates="restaurant", cascade="all, delete-orphan"
    )

    opening_hours = db.relationship(
        "OpeningHour", back_populates="restaurant", cascade="all, delete-orphan"
    )

    reviews = db.relationship(
        "Review", back_populates="restaurant", cascade="all, delete-orphan"
    )

    bookmarks = db.relationship(
        "Bookmark", back_populates="restaurant", cascade="all, delete-orphan"
    )


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), nullable=False
    )

    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image_url = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    restaurant = db.relationship("Restaurant", back_populates="menu_items")


class OpeningHour(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), nullable=False
    )

    day_of_week = db.Column(db.Integer, nullable=False)
    day_label = db.Column(db.String(20), nullable=False)

    open_time = db.Column(db.String(20))
    close_time = db.Column(db.String(20))
    is_closed = db.Column(db.Boolean, nullable=False, default=False)

    restaurant = db.relationship("Restaurant", back_populates="opening_hours")

    __table_args__ = (
        db.UniqueConstraint(
            "restaurant_id", "day_of_week", name="unique_restaurant_day"
        ),
    )


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), nullable=False
    )

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    restaurant = db.relationship("Restaurant", back_populates="reviews")

    user = db.relationship("User", back_populates="reviews")

    photos = db.relationship(
        "ReviewPhoto", back_populates="review", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.CheckConstraint(
            "rating >= 1 AND rating <= 5", name="check_review_rating_range"
        ),
    )


class ReviewPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    review_id = db.Column(db.Integer, db.ForeignKey("review.id"), nullable=False)

    image_url = db.Column(db.String(255), nullable=False)

    review = db.relationship("Review", back_populates="photos")


class BookmarkCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="bookmark_collections")

    bookmarks = db.relationship(
        "Bookmark", back_populates="collection", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="unique_collection_name_per_user"),
    )


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    collection_id = db.Column(
        db.Integer, db.ForeignKey("bookmark_collection.id"), nullable=False
    )

    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), nullable=False
    )

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    collection = db.relationship("BookmarkCollection", back_populates="bookmarks")

    restaurant = db.relationship("Restaurant", back_populates="bookmarks")

    __table_args__ = (
        db.UniqueConstraint(
            "collection_id", "restaurant_id", name="unique_restaurant_per_collection"
        ),
    )
