from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.habit import Completion, Habit


def compute_streak(completed_days: list[date], today: date) -> int:
    """Consecutive days ending today or yesterday. A gap of 2+ days breaks it."""
    days = set(completed_days)
    if not days:
        return 0

    if today in days:
        cursor = today
    elif today - timedelta(days=1) in days:
        cursor = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def start_of_week(day: date) -> date:
    """Monday of the week containing `day`."""
    return day - timedelta(days=day.weekday())


def count_completions_in_week(completed_days: list[date], today: date) -> int:
    week_start = start_of_week(today)
    return sum(1 for day in completed_days if week_start <= day <= today)


def create_habit(
    db: Session,
    name: str,
    category: str = "General",
    target_per_week: int = 7,
    notes: str | None = None,
) -> Habit:
    habit = Habit(name=name, category=category, target_per_week=target_per_week, notes=notes)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def list_habits(
    db: Session, category: str | None = None, include_archived: bool = False
) -> list[Habit]:
    query = db.query(Habit)
    if category:
        query = query.filter(Habit.category == category)
    if not include_archived:
        query = query.filter(Habit.archived.is_(False))
    return query.order_by(Habit.id).all()


def list_categories(db: Session) -> list[str]:
    rows = db.query(Habit.category).distinct().order_by(Habit.category).all()
    return [row[0] for row in rows]


def get_habit(db: Session, habit_id: int) -> Habit | None:
    return db.get(Habit, habit_id)


def complete_habit(db: Session, habit: Habit, today: date) -> Habit:
    already_done = db.query(Completion).filter_by(habit_id=habit.id, day=today).first()
    if not already_done:
        db.add(Completion(habit_id=habit.id, day=today))
        db.commit()
    return habit


def update_habit(
    db: Session,
    habit: Habit,
    name: str | None = None,
    category: str | None = None,
    target_per_week: int | None = None,
    notes: str | None = None,
    archived: bool | None = None,
) -> Habit:
    if name is not None:
        habit.name = name
    if category is not None:
        habit.category = category
    if target_per_week is not None:
        habit.target_per_week = target_per_week
    if notes is not None:
        habit.notes = notes
    if archived is not None:
        habit.archived = archived
    db.commit()
    db.refresh(habit)
    return habit


def delete_habit(db: Session, habit: Habit) -> None:
    db.delete(habit)
    db.commit()


def get_stats(db: Session, today: date) -> dict:
    summaries = [to_summary(habit, today) for habit in list_habits(db)]

    weekly_target_total = sum(s["target_per_week"] for s in summaries)
    weekly_completed_total = sum(s["completed_this_week"] for s in summaries)

    by_category: dict[str, int] = {}
    for summary in summaries:
        by_category[summary["category"]] = by_category.get(summary["category"], 0) + 1

    return {
        "total_habits": len(summaries),
        "completed_today": sum(1 for s in summaries if s["completed_today"]),
        "active_streaks": sum(1 for s in summaries if s["streak"] > 0),
        "best_streak": max((s["streak"] for s in summaries), default=0),
        "total_completions": sum(len(s["completed_days"]) for s in summaries),
        "weekly_completion_rate": (
            round(weekly_completed_total / weekly_target_total * 100)
            if weekly_target_total
            else 0
        ),
        "by_category": by_category,
    }


def is_at_risk(
    target_per_week: int, completed_this_week: int, completed_today: bool, today: date
) -> bool:
    """True if hitting the weekly target now requires completing every
    remaining day of the week, including today.

    Not just "behind" -- there is still enough of the week left to recover
    unless every remaining day counts. Never at risk once today is already
    done, since today's own opportunity is spent either way.
    """
    if completed_today:
        return False
    remaining_needed = target_per_week - completed_this_week
    if remaining_needed <= 0:
        return False
    days_left_in_week = 7 - today.weekday()
    return remaining_needed >= days_left_in_week


def to_summary(habit: Habit, today: date) -> dict:
    completed_days = [c.day for c in habit.completions]
    completed_this_week = count_completions_in_week(completed_days, today)
    completed_today = today in completed_days
    return {
        "id": habit.id,
        "name": habit.name,
        "category": habit.category,
        "target_per_week": habit.target_per_week,
        "notes": habit.notes,
        "archived": habit.archived,
        "completed_this_week": completed_this_week,
        "streak": compute_streak(completed_days, today),
        "completed_today": completed_today,
        "completed_days": sorted(completed_days),
        "at_risk": is_at_risk(habit.target_per_week, completed_this_week, completed_today, today),
    }
