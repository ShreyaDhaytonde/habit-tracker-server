from datetime import date, timedelta

from app.services.habit_service import compute_streak, count_completions_in_week, start_of_week


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


def test_start_of_week_returns_monday():
    # 2026-01-10 is a Saturday.
    assert start_of_week(date(2026, 1, 10)) == date(2026, 1, 5)


def test_start_of_week_is_idempotent_on_monday():
    monday = date(2026, 1, 5)
    assert start_of_week(monday) == monday


def test_count_completions_in_week_only_counts_current_week():
    today = date(2026, 1, 10)  # Saturday, week starts Monday 2026-01-05
    days = [
        date(2026, 1, 5),
        date(2026, 1, 7),
        today,
        date(2026, 1, 4),  # last week, excluded
    ]
    assert count_completions_in_week(days, today) == 3


def test_count_completions_in_week_zero_when_no_completions_this_week():
    assert count_completions_in_week([date(2026, 1, 1)], date(2026, 1, 10)) == 0
