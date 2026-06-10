from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models import Promotion
from app.routers.auth import get_current_user

router = APIRouter()

class PromotionCreate(BaseModel):
    title: str
    description: str
    discount_percent: float
    bonus_percent: float = 5.0
    start_date: datetime
    end_date: datetime

@router.get("/")
def get_promotions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Promotion).all()

@router.get("/active")
def get_active_promotions(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    return db.query(Promotion).filter(
        Promotion.is_active == True,
        Promotion.start_date <= now,
        Promotion.end_date >= now
    ).all()

@router.post("/")
def create_promotion(data: PromotionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    promo = Promotion(**data.dict())
    db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo

@router.put("/{promo_id}/toggle")
def toggle_promotion(promo_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Aksiya topilmadi")
    promo.is_active = not promo.is_active
    db.commit()
    return {"message": f"Aksiya {'yoqildi' if promo.is_active else 'o\'chirildi'}"}

@router.delete("/{promo_id}")
def delete_promotion(promo_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Aksiya topilmadi")
    db.delete(promo)
    db.commit()
    return {"message": "Aksiya o'chirildi"}
