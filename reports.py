from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Company, Order, Bonus, Promotion
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    total_companies = db.query(func.count(Company.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    total_revenue = db.query(func.sum(Order.amount)).scalar() or 0
    total_bonuses = db.query(func.sum(Bonus.amount)).scalar() or 0
    active_promotions = db.query(func.count(Promotion.id)).filter(Promotion.is_active == True).scalar()

    top_companies = db.query(
        Company.id, Company.name, Company.bonus_balance,
        func.sum(Order.amount).label("total_spent")
    ).join(Order, Order.company_id == Company.id, isouter=True)\
     .group_by(Company.id).order_by(func.sum(Order.amount).desc()).limit(5).all()

    return {
        "total_companies": total_companies,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "total_bonuses_given": round(total_bonuses, 2),
        "active_promotions": active_promotions,
        "top_companies": [
            {"id": c.id, "name": c.name, "bonus_balance": c.bonus_balance, "total_spent": c.total_spent or 0}
            for c in top_companies
        ]
    }
