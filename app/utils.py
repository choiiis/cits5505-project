from datetime import datetime


def make_star_text(rating):
    full_stars = int(round(rating))
    full_stars = max(0, min(5, full_stars))
    empty_stars = 5 - full_stars

    return "★" * full_stars + "☆" * empty_stars


def get_current_day_abbr():
    return datetime.now().strftime("%a")


def mark_today(opening_hours):
    today = get_current_day_abbr()

    for item in opening_hours:
        item["is_today"] = item["day"] == today

    return opening_hours
