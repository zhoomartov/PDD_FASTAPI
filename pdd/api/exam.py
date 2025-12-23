from fastapi import FastAPI, HTTPException, APIRouter, Depends, status
from pdd.db.models import Exam
from pdd.db.schema import ExamSchema
from pdd.db.database import SessionLocal
from typing import List

exam_router = APIRouter(prefix="/exam", tags=["Exam"])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@exam_router.post("/", response_model=ExamSchema, status_code=201)
def create_exam():
    return {"message": "POST /exam — создание экзамена"}


@exam_router.get("/", response_model=List[ExamSchema])
def list_exams():
    return [{"message": "GET /exam — список экзаменов"}]


@exam_router.get("/{exam_id}", response_model=ExamSchema)
def get_exam(exam_id: int):
    return {"id": exam_id, "message": "GET /exam/{exam_id} — просмотр экзамена"}


@exam_router.put("/{exam_id}", response_model=dict)
def update_exam(exam_id: int):
    return {"id": exam_id, "message": "PUT /exam/{exam_id} — обновление экзамена"}


@exam_router.delete("/{exam_id}", status_code=204)
def delete_exam(exam_id: int):
    return None