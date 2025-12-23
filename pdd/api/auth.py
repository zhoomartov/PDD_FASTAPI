from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import hashlib
from jose import jwt
from passlib.context import CryptContext
from fastapi.security import (OAuth2PasswordBearer,
                              OAuth2PasswordRequestForm)
from pdd.db.database import SessionLocal
from pdd.db.models import User, RefreshToken
from pdd.db.schema import (
    UserSchema,
    UserLoginSchema,
    UserCreateSchema,
)
from pdd.db.config import (
    ALGORITHM,SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS)


auth_router = APIRouter(prefix='/auth', tags=['Auth'])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode =  data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': expire})
    return jwt.encode( to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    sha = hashlib.sha256(plain_password.encode('utf-8')).digest()
    return pwd_context.verify(sha, hashed_password)

def get_password_hash(password: str) -> str:
    sha = hashlib.sha256(password.encode("utf-8")).digest()
    return pwd_context.hash(sha)



@auth_router.post('/register', response_model=dict)
async def auth_register(user: UserCreateSchema,
                        db: Session = Depends(get_db)):
    check_user = db.query(User).filter(User.username == user.username).first()

    if check_user:
        raise HTTPException(status_code=404, detail='User already exists')

    check_email = db.query(User).filter(User.email == user.email).first()
    if check_email:
        raise HTTPException(status_code=404, detail='Email already exists')

    hash_password = get_password_hash(user.password)
    user_db = User(
        email=user.email,
        username=user.username,
        password=hash_password,
    )

    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return {'message': 'created'}


@auth_router.post('/login')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Маалымат туура эмес")

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    new_token = RefreshToken(user_id=user.id, token=refresh_token)
    db.add(new_token)
    db.commit()

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}



@auth_router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()

    if not stored_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    db.delete(stored_token)
    db.commit()

    return {'message': 'Вышли'}

@auth_router.post("/refresh")
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    token_entry = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not token_entry:
        raise HTTPException(status_code=404, detail='Token not found')

    access_token = create_access_token({'sub': token_entry.user_id})

    return {'access_token': access_token, 'token_type': 'bearer'}