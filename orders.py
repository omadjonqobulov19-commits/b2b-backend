from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Order, Company, Bonus, Promotion
from app.routers.auth import get_current_user
from datetime import datetime

router = APIRouter()

class OrderCreate(BaseModel):
    company_id: int
    amount: float
    description: str

@router.get("/")
def get_orders(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    orders = db.query(Order).all()
    result = []
    for o in orders:
        result.append({
            "id": o.id, "company_id": o.company_id,
            "company_name": o.company.name if o.company else "",
            "amount": o.amount, "description": o.description,
            "status": o.status, "created_at": o.created_at
        })
    return result

@router.post("/")
def create_order(data: OrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    company = db.query(Company).filter(Company.id == data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")

    order = Order(company_id=data.company_id, amount=data.amount, description=data.description, status="completed")
    db.add(order)
    db.commit()
    db.refresh(order)

    now = datetime.utcnow()
    promo = db.query(Promotion).filter(
        Promotion.is_active == True,
        Promotion.start_date <= now,
        Promotion.end_date >= now
    ).first()

    bonus_percent = promo.bonus_percent if promo else 5.0
    bonus_amount = data.amount * (bonus_percent / 100)

    bonus = Bonus(
        company_id=data.company_id,
        order_id=order.id,
        amount=bonus_amount,
        description=f"Buyurtma #{order.id} uchun {bonus_percent}% bonus"
    )
    db.add(bonus)
    company.bonus_balance += bonus_amount
    db.commit()

    return {"order": order, "bonus_added": bonus_amount, "bonus_percent": bonus_percent}

@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return order
