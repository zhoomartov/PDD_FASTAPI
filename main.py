from fastapi import FastAPI
import uvicorn
from pdd.api import (model_pdd, user, auth, video,
                         exam, question, category)
from pdd.api.model_pdd import predict_router



pdd_app = FastAPI()
pdd_app.include_router(predict_router)
pdd_app.include_router(user.user_router)
pdd_app.include_router(auth.auth_router)
pdd_app.include_router(exam.exam_router)
pdd_app.include_router(question.question_router)
pdd_app.include_router(category.category_router)
pdd_app.include_router(video.video_router)






if __name__ == '__main__':
    uvicorn.run(pdd_app, host='127.0.0.1', port=8000)