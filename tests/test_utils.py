import unittest

from app.utils import make_star_text, mark_today


class UtilityFunctionTests(unittest.TestCase):
    def test_make_star_text_rounds_to_nearest_star(self):
        self.assertEqual(make_star_text(3.6), "★★★★☆")

    def test_make_star_text_caps_above_five(self):
        self.assertEqual(make_star_text(8), "★★★★★")

    def test_make_star_text_floors_below_zero(self):
        self.assertEqual(make_star_text(-2), "☆☆☆☆☆")

    def test_make_star_text_handles_zero(self):
        self.assertEqual(make_star_text(0), "☆☆☆☆☆")

    def test_mark_today_sets_exactly_matching_day(self):
        opening_hours = [
            {"day": "NotToday", "is_today": True},
            {"day": "Today", "is_today": False},
        ]

        import app.utils as utils

        original_get_current_day_abbr = utils.get_current_day_abbr
        utils.get_current_day_abbr = lambda: "Today"

        try:
            marked_hours = mark_today(opening_hours)
        finally:
            utils.get_current_day_abbr = original_get_current_day_abbr

        self.assertFalse(marked_hours[0]["is_today"])
        self.assertTrue(marked_hours[1]["is_today"])


if __name__ == "__main__":
    unittest.main()
