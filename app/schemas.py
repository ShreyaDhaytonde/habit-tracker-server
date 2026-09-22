from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PriorityLevel = Literal["Low", "Medium", "High"]


class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str = Field(default="General", min_length=1, max_length=50)
    priority: PriorityLevel = Field(default="Medium")
    target_per_week: int = Field(default=7, ge=1, le=7)
    notes: str | None = Field(default=None, max_length=1000)


class HabitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    priority: PriorityLevel | None = Field(default=None)
    target_per_week: int | None = Field(default=None, ge=1, le=7)
    notes: str | None = Field(default=None, max_length=1000)
    archived: bool | None = Field(default=None)
    pinned: bool | None = Field(default=None)


class HabitStats(BaseModel):
    total_habits: int
    completed_today: int
    skipped_today: int
    active_streaks: int
    best_streak: int
    total_completions: int
    weekly_completion_rate: int
    pinned_count: int
    by_category: dict[str, int]
    by_priority: dict[str, int]


class HabitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    priority: str
    target_per_week: int
    notes: str | None
    archived: bool
    pinned: bool
    completed_this_week: int
    streak: int
    longest_streak: int
    completed_today: bool
    completed_days: list[date]
    skipped_today: bool
    skipped_days: list[date]
    at_risk: bool
