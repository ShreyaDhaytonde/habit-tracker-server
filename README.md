# Habit Tracker API

FastAPI + SQLAlchemy backend for tracking daily habits and streaks.

## Endpoints

- `GET /habits` — list habits with current streak and today's completion status
- `POST /habits` — create a habit (`{"name": "..."}`)
- `POST /habits/{id}/complete` — mark a habit done for today (idempotent)
- `DELETE /habits/{id}` — remove a habit
- `GET /health` — health check

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Test

```bash
pytest
```
