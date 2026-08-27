from datetime import date, timedelta

from app.services.habit_service import compute_streak


def test_streak_zero_when_no_completions():
    assert compute_streak([], date(2026, 1, 10)) == 0


def test_streak_counts_consecutive_days_including_today():
    today = date(2026, 1, 10)
    days = [today, today - timedelta(days=1), today - timedelta(days=2)]
    assert compute_streak(days, today) == 3


def test_streak_still_counts_if_yesterday_done_but_not_today_yet():
    today = date(2026, 1, 10)
    days = [today - timedelta(days=1), today - timedelta(days=2)]
    assert compute_streak(days, today) == 2


def test_streak_breaks_on_gap():
    today = date(2026, 1, 10)
    days = [today, today - timedelta(days=3)]
    assert compute_streak(days, today) == 1


def test_streak_zero_if_last_completion_older_than_yesterday():
    today = date(2026, 1, 10)
    days = [today - timedelta(days=2)]
    assert compute_streak(days, today) == 0
