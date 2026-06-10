from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
SECRET_KEY = os.getenv("SECRET_KEY", "b2b-secret-key-2024")
ALGORITHM = "HS256"

class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str
    is_admin: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str
    is_admin: bool
    full_name: str

def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(hours=24)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Foydalanuvchi topilmadi")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token yaroqsiz")

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email allaqachon ro'yxatdan o'tgan")
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=pwd_context.hash(user_data.password),
        is_admin=user_data.is_admin
    )
    db.add(user)
    db.commit()
    return {"message": "Muvaffaqiyatli ro'yxatdan o'tildi"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Email yoki parol noto'g'ri")
    token = create_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "is_admin": user.is_admin, "full_name": user.full_name}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "full_name": current_user.full_name, "is_admin": current_user.is_admin}
