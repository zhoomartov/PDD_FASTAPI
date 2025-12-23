from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import QuestionDifficulty, ExamStatus

class UserSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str



class CategorySchema(BaseModel):
    id: int
    category_name: str

    class Config:
        from_attributes = True



class AnswerOptionCreate(BaseModel):
    text: str
    is_correct: bool = False


class QuestionCreate(BaseModel):
    text: str
    difficulty: QuestionDifficulty
    category_id: int
    explanation: Optional[str] = None
    answer_options: List[AnswerOptionCreate]


class AnswerOptionOut(BaseModel):
    id: str
    text: str

    class Config:
        from_attributes = True


class QuestionListItem(BaseModel):
    id: str
    text: str
    image: Optional[str] = None
    options: List[AnswerOptionOut]

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    items: List[QuestionListItem]


class QuestionDetailResponse(BaseModel):
    id: str
    text: str
    explanation: Optional[str] = None
    correct_option_id: str



class ExamSchema(BaseModel):
    id: int
    user_id: int
    score: int
    status: ExamStatus
    started_at: datetime
    finished_at: Optional[datetime]
    question_id: int

    class Config:
        from_attributes = True



class VideoSchema(BaseModel):
    id: int
    title: str
    description: Optional[str]
    url: str

    class Config:
        from_attributes = True



class AIPredictionLogSchema(BaseModel):
    id: int
    user_id: int
    image_url: str
    predicted_label: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True
