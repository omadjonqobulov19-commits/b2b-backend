from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Bonus, Company
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/")
def get_bonuses(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    bonuses = db.query(Bonus).all()
    result = []
    for b in bonuses:
        result.append({
            "id": b.id,
            "company_id": b.company_id,
            "company_name": b.company.name if b.company else "",
            "order_id": b.order_id,
            "amount": b.amount,
            "description": b.description,
            "created_at": b.created_at
        })
    return result

@router.get("/company/{company_id}")
def get_company_bonuses(company_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")
    bonuses = db.query(Bonus).filter(Bonus.company_id == company_id).all()
    return {
        "company": company.name,
        "bonus_balance": company.bonus_balance,
        "history": bonuses
    }
