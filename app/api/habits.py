from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import HabitCreate, HabitOut
from app.services import habit_service

router = APIRouter(prefix="/habits", tags=["habits"])


@router.get("", response_model=list[HabitOut])
def list_habits(db: Session = Depends(get_db)):
    today = date.today()
    return [habit_service.to_summary(h, today) for h in habit_service.list_habits(db)]


@router.post("", response_model=HabitOut, status_code=201)
def create_habit(payload: HabitCreate, db: Session = Depends(get_db)):
    habit = habit_service.create_habit(db, payload.name)
    return habit_service.to_summary(habit, date.today())


@router.post("/{habit_id}/complete", response_model=HabitOut)
def complete_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = habit_service.get_habit(db, habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    today = date.today()
    habit_service.complete_habit(db, habit, today)
    return habit_service.to_summary(habit, today)


@router.delete("/{habit_id}", status_code=204)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = habit_service.get_habit(db, habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    habit_service.delete_habit(db, habit)
