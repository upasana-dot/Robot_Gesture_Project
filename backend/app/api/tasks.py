
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Task

router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"],
)


@router.get("/")
def get_tasks(db: Session = Depends(get_db)):
    """Get all tasks with their action steps."""

    tasks = (
        db.query(Task)
        .options(selectinload(Task.actions))
        .order_by(Task.id.desc())
        .all()
    )

    return tasks


@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a single task with its action steps."""

    task = (
        db.query(Task)
        .options(selectinload(Task.actions))
        .filter(Task.id == task_id)
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found",
        )

    return task
