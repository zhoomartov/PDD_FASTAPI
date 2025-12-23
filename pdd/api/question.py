from fastapi import APIRouter, HTTPException, status, Query,Depends
from fastapi_pagination import Page, paginate, Params
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from typing import Optional, List
from pdd.db.database import SessionLocal
from pdd.db.models import Question, AnswerOption, Category, QuestionDifficulty
from pdd.db.schema import QuestionDifficulty, AnswerOptionOut, AnswerOptionCreate, QuestionCreate,QuestionDetailResponse,QuestionListResponse, QuestionListItem


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


question_router = APIRouter(prefix="/questions", tags=["Questions PDD"])


# === Получение списка вопросов (доступно всем) ===
@question_router.get("", response_model=QuestionListResponse)
def get_questions(
    category: Optional[str] = Query(None, description="Категория, например A или B"),
    difficulty: Optional[str] = Query(None, description="easy, medium, advanced"),
    params: Params = Params(),
    db: Session = Depends(get_db),
):
    query = select(Question).options(selectinload(Question.answer_options))

    if category:
        query = query.join(Category).where(Category.category_name == category)

    if difficulty:
        try:
            diff = QuestionDifficulty[difficulty.lower()]
            query = query.where(Question.difficulty == diff)
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail="Неверное значение difficulty. Доступно: easy, medium, advanced"
            )

    result = paginate(db, query, params=params)

    items = []
    for q in result.items:
        options = [{"id": str(opt.id), "text": opt.text} for opt in q.answer_options]
        items.append({
            "id": str(q.id),
            "text": q.text,
            "image": None,
            "options": options
        })

    return {"items": items}


# === Детальная информация о вопросе (доступно всем) ===
@question_router.get("/{question_id}", response_model=QuestionDetailResponse)
def get_question_detail(question_id: int, db: Session = Depends(get_db)):
    question = db.get(Question, question_id, options=[selectinload(Question.answer_options)])
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    correct_option = next((opt for opt in question.answer_options if opt.is_correct), None)
    if not correct_option:
        raise HTTPException(status_code=500, detail="У вопроса нет правильного ответа")

    return QuestionDetailResponse(
        id=str(question.id),
        text=question.text,
        explanation=question.explanation,
        correct_option_id=str(correct_option.id)
    )


# === Создание вопроса (доступно всем, без авторизации) ===
@question_router.post("/", status_code=status.HTTP_201_CREATED)
def create_question(data: QuestionCreate, db: Session = Depends(get_db)):
    # Проверяем существование категории
    category = db.get(Category, data.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="Категория не найдена")

    # Создаём вопрос
    question = Question(
        text=data.text,
        difficulty=data.difficulty,
        explanation=data.explanation,
        category_id=data.category_id
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    # Добавляем варианты ответов
    for opt in data.answer_options:
        answer_option = AnswerOption(
            text=opt.text,
            is_correct=opt.is_correct,
            question_id=question.id
        )
        db.add(answer_option)

    db.commit()
    db.refresh(question)

    return {"message": "Вопрос успешно создан", "question_id": question.id}


# === Обновление вопроса (доступно всем) ===
@question_router.put("/{question_id}")
def update_question(question_id: int, data: QuestionCreate, db: Session = Depends(get_db)):
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    # Обновляем основные поля
    question.text = data.text
    question.difficulty = data.difficulty
    question.explanation = data.explanation
    question.category_id = data.category_id

    # Удаляем старые варианты ответов
    db.query(AnswerOption).filter(AnswerOption.question_id == question_id).delete()

    # Добавляем новые
    for opt in data.answer_options:
        answer_option = AnswerOption(
            text=opt.text,
            is_correct=opt.is_correct,
            question_id=question.id
        )
        db.add(answer_option)

    db.commit()
    db.refresh(question)

    return {"message": "Вопрос успешно обновлён"}


# === Удаление вопроса (доступно всем) ===
@question_router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    db.delete(question)
    db.commit()
    return None
