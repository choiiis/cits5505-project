from app import db
from app.models import Bookmark, BookmarkCollection, CollectionSubscription, Restaurant, User
from app.routes import format_bookmark_collection, format_restaurant_card
from tests.base import DatabaseTestCase


class BookmarkHelperTests(DatabaseTestCase):
    def test_format_restaurant_card_uses_suburb_before_address(self):
        restaurant = Restaurant(
            id=7,
            name="Laneway Pizza Co.",
            category="Italian",
            description="Wood-fired pizza.",
            address="Barrack Street",
            suburb="Perth CBD",
            average_rating=4.74,
            review_count=18,
            status="approved",
        )

        with self.app_context.app.test_request_context():
            card = format_restaurant_card(restaurant)

        self.assertEqual(card["location"], "Perth CBD")
        self.assertEqual(card["rating"], 4.7)
        self.assertEqual(card["restaurant_id"], 7)

    def test_format_bookmark_collection_counts_only_approved_restaurants(self):
        user = User(email="owner@example.com", username="Owner", password_hash="hash")
        subscriber = User(
            email="subscriber@example.com",
            username="Subscriber",
            password_hash="hash",
        )
        approved = Restaurant(
            name="Approved Cafe",
            category="Cafe",
            description="Open to users.",
            address="1 Test Street",
            average_rating=4.2,
            review_count=3,
            status="approved",
        )
        pending = Restaurant(
            name="Pending Cafe",
            category="Cafe",
            description="Not yet visible.",
            address="2 Test Street",
            average_rating=5.0,
            review_count=1,
            status="pending",
        )
        collection = BookmarkCollection(
            user=user,
            name="Weekend brunch",
            description="Cafe ideas.",
            is_public=True,
        )

        db.session.add_all([user, subscriber, approved, pending, collection])
        db.session.commit()
        db.session.add_all(
            [
                Bookmark(collection_id=collection.id, restaurant_id=approved.id),
                Bookmark(collection_id=collection.id, restaurant_id=pending.id),
                CollectionSubscription(collection_id=collection.id, user_id=subscriber.id),
            ]
        )
        db.session.commit()

        with self.app_context.app.test_request_context():
            card = format_bookmark_collection(
                collection,
                is_subscribed=True,
                current_user_id=subscriber.id,
            )

        self.assertEqual(card["restaurant_count"], 1)
        self.assertEqual(card["subscriber_count"], 1)
        self.assertTrue(card["is_subscribed"])
        self.assertFalse(card["is_owner"])
        self.assertEqual(card["creator"], "Owner")


if __name__ == "__main__":
    import unittest

    unittest.main()
