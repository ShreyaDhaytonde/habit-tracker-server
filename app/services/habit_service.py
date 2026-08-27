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


def create_habit(db: Session, name: str) -> Habit:
    habit = Habit(name=name)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def list_habits(db: Session) -> list[Habit]:
    return db.query(Habit).order_by(Habit.id).all()


def get_habit(db: Session, habit_id: int) -> Habit | None:
    return db.get(Habit, habit_id)


def complete_habit(db: Session, habit: Habit, today: date) -> Habit:
    already_done = db.query(Completion).filter_by(habit_id=habit.id, day=today).first()
    if not already_done:
        db.add(Completion(habit_id=habit.id, day=today))
        db.commit()
    return habit


def delete_habit(db: Session, habit: Habit) -> None:
    db.delete(habit)
    db.commit()


def to_summary(habit: Habit, today: date) -> dict:
    completed_days = [c.day for c in habit.completions]
    return {
        "id": habit.id,
        "name": habit.name,
        "streak": compute_streak(completed_days, today),
        "completed_today": today in completed_days,
        "completed_days": sorted(completed_days),
    }
