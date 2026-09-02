from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50), default="General", server_default="General")
    target_per_week: Mapped[int] = mapped_column(Integer, default=7, server_default="7")

    completions: Mapped[list["Completion"]] = relationship(
        back_populates="habit", cascade="all, delete-orphan", order_by="Completion.day"
    )


class Completion(Base):
    __tablename__ = "completions"
    __table_args__ = (UniqueConstraint("habit_id", "day", name="uq_habit_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))
    day: Mapped[date] = mapped_column(Date)

    habit: Mapped["Habit"] = relationship(back_populates="completions")
