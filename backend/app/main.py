
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.tasks import router as tasks_router
from app.database import Base, engine, get_db
from app.schemas import TaskRequest
from app.services.task_service import create_and_execute_task


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAST API",
    description="Robotic Action Sequence Transformer",
    version="0.1.0",
)

app.include_router(tasks_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "project": "RAST",
        "message": "Robotic Action Sequence Transformer API is running.",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/tasks")
def create_task(
    request: TaskRequest,
    db: Session = Depends(get_db),
):
    try:
        return create_and_execute_task(
            instruction=request.instruction,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )
