from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str = Field(default="General", min_length=1, max_length=50)
    target_per_week: int = Field(default=7, ge=1, le=7)
    notes: str | None = Field(default=None, max_length=1000)


class HabitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    target_per_week: int | None = Field(default=None, ge=1, le=7)
    notes: str | None = Field(default=None, max_length=1000)
    archived: bool | None = Field(default=None)


class HabitStats(BaseModel):
    total_habits: int
    completed_today: int
    active_streaks: int
    best_streak: int
    total_completions: int
    weekly_completion_rate: int
    by_category: dict[str, int]


class HabitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    target_per_week: int
    notes: str | None
    archived: bool
    completed_this_week: int
    streak: int
    completed_today: bool
    completed_days: list[date]
    at_risk: bool
