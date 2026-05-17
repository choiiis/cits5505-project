from app import db
from app.models import Restaurant, Review, User
from app.routes import build_review_summary, refresh_restaurant_rating_summary
from tests.base import DatabaseTestCase


class ReviewHelperTests(DatabaseTestCase):
    def test_build_review_summary_handles_empty_reviews(self):
        summary = build_review_summary([])

        self.assertEqual(summary["average_rating"], 0.0)
        self.assertEqual(summary["total_reviews"], 0)
        self.assertTrue(all(item["percentage"] == 0 for item in summary["distribution"]))

    def test_build_review_summary_calculates_average_and_distribution(self):
        reviews = [
            Review(rating=5, content="Excellent"),
            Review(rating=4, content="Good"),
            Review(rating=4, content="Still good"),
            Review(rating=1, content="Poor"),
        ]

        summary = build_review_summary(reviews)

        self.assertEqual(summary["average_rating"], 3.5)
        self.assertEqual(summary["total_reviews"], 4)
        self.assertEqual(summary["distribution"][0]["stars"], 5)
        self.assertEqual(summary["distribution"][0]["percentage"], 25)
        self.assertEqual(summary["distribution"][1]["stars"], 4)
        self.assertEqual(summary["distribution"][1]["count"], 2)

    def test_refresh_restaurant_rating_summary_ignores_hidden_reviews(self):
        user = User(
            email="reviewer@example.com",
            username="Reviewer",
            password_hash="hash",
        )
        restaurant = Restaurant(
            name="Test Restaurant",
            category="Cafe",
            address="1 Test Street",
            status="approved",
        )
        db.session.add_all([user, restaurant])
        db.session.commit()

        db.session.add_all(
            [
                Review(
                    restaurant_id=restaurant.id,
                    user_id=user.id,
                    rating=5,
                    content="Great",
                    status="active",
                ),
                Review(
                    restaurant_id=restaurant.id,
                    user_id=user.id,
                    rating=1,
                    content="Hidden",
                    status="hidden",
                ),
            ]
        )
        db.session.commit()

        refresh_restaurant_rating_summary(restaurant)

        self.assertEqual(restaurant.review_count, 1)
        self.assertEqual(restaurant.average_rating, 5.0)


if __name__ == "__main__":
    import unittest

    unittest.main()
