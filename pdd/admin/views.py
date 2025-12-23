from sqladmin import ModelView
from pdd.db.models import User, Category, Question, AnswerOption, Exam, Video

class UserProfileAdmin(ModelView , model = User):
    column_list = [User.username , User.email , User.password]

class CategoryAdmin(ModelView , model=Category):
    column_list = [Category.category_name]

class QuestionAdmin(ModelView , model = Question):
    column_list = [Question.text , Question.difficulty , Question.explanation]

class AnswerAdmin(ModelView , model = AnswerOption):
    column_list = [AnswerOption.text , AnswerOption.is_correct]

# class ExamAdmin(ModelView , model = Exam):
#     column_list = [Exam.score , Exam.status]

class VideoAdmin(ModelView , model = Video):
    column_list = [Video.title , Video.description]