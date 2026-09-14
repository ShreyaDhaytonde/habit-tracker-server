from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50), default="General", server_default="General")
    target_per_week: Mapped[int] = mapped_column(Integer, default=7, server_default="7")
    notes: Mapped[str | None] = mapped_column(String(1000), default=None, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")

    completions: Mapped[list["Completion"]] = relationship(
        back_populates="habit", cascade="all, delete-orphan", order_by="Completion.day"
    )
    skips: Mapped[list["Skip"]] = relationship(
        back_populates="habit", cascade="all, delete-orphan", order_by="Skip.day"
    )


class Completion(Base):
    __tablename__ = "completions"
    __table_args__ = (UniqueConstraint("habit_id", "day", name="uq_habit_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))
    day: Mapped[date] = mapped_column(Date)

    habit: Mapped["Habit"] = relationship(back_populates="completions")


class Skip(Base):
    """A rest/freeze day: preserves the streak without counting as a
    completion. Stored separately from Completion (rather than a flag on
    it) so a day is unambiguously completed, skipped, or neither, and so
    this ships without any migration -- a new table is picked up by the
    existing `Base.metadata.create_all`."""

    __tablename__ = "skips"
    __table_args__ = (UniqueConstraint("habit_id", "day", name="uq_habit_skip_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))
    day: Mapped[date] = mapped_column(Date)

    habit: Mapped["Habit"] = relationship(back_populates="skips")
