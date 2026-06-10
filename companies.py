from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Company
from app.routers.auth import get_current_user

router = APIRouter()

class CompanyCreate(BaseModel):
    name: str
    stir: str
    phone: str
    address: str

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

@router.get("/")
def get_companies(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Company).all()

@router.post("/")
def create_company(data: CompanyCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if db.query(Company).filter(Company.stir == data.stir).first():
        raise HTTPException(status_code=400, detail="Bu STIR bilan kompaniya mavjud")
    company = Company(**data.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.get("/{company_id}")
def get_company(company_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")
    return company

@router.put("/{company_id}")
def update_company(company_id: int, data: CompanyUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")
    for key, value in data.dict(exclude_none=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company

@router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")
    db.delete(company)
    db.commit()
    return {"message": "Kompaniya o'chirildi"}
