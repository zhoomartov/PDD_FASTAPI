from fastapi import APIRouter , Depends,HTTPException
from pdd.db.schema import VideoSchema
from pdd.db.models import Video
from sqlalchemy.orm import Session
from pdd.db.database import SessionLocal
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

video_router = APIRouter(prefix='/video' , tags=['Video'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@video_router.post('/' , response_model=VideoSchema)
async def create_video(video : VideoSchema ,db: Session= Depends(get_db)):
    data_db =Video(**video.dict())
    db.add(data_db)
    db.commit()
    db.refresh(data_db)
    return data_db

@video_router.get('/',response_model=Page[VideoSchema])
async def video_list(db: Session = Depends(get_db)):
    query = db.query(Video)
    return paginate(db, query)


@video_router.get('/{video_id}',response_model =VideoSchema)
async def video_detail(video_id: int, db: Session = Depends(get_db)):
    db_video = db.query(Video).filter(Video.id == video_id).first()

    if db_video is None:
        raise HTTPException(status_code=404, detail = 'Not Found')
    return db_video

@video_router.put('/{video_id}/' , response_model=dict)
async def video_update(video: VideoSchema , video_id : int,
                        db: Session = Depends(get_db)):
    db_data = db.query(Video).filter(Video.id == video_id).first()
    if not db_data:
        raise HTTPException(status_code=404 , detail='Not Found')
    for lesson_key , lesson_value in video.dict().items():
        setattr(db_data , lesson_key,lesson_value)

        db.commit()
        db.refresh(db_data)

        return {'message':'Успешно!'}

@video_router.delete('/{video_id}',response_model =VideoSchema)
async def video_delete(video_id: int, db: Session = Depends(get_db)):
    db_data = db.query(Video).filter(Video.id == video_id).first()

    if db_data is None:
        raise HTTPException(status_code=404, detail = 'Not Found')
    db.delete(db_data)
    db.commit()
    return {'massage' : 'Удалено!'}