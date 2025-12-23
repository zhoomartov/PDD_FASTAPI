from .views import *
from fastapi import FastAPI
from sqladmin import Admin
from pdd.db.database import engine

def setup_admin(pdd_app:FastAPI):
    admin = Admin(pdd_app, engine)
    admin.add_view(UserProfileAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(QuestionAdmin)
    admin.add_view(AnswerAdmin)
    # admin.add_view(ExamAdmin)
    admin.add_view(VideoAdmin)