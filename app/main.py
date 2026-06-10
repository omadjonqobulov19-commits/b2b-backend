from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, companies, orders, bonuses, promotions, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="B2B Aksiya va Bonuslar Tizimi", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(bonuses.router, prefix="/api/bonuses", tags=["Bonuses"])
app.include_router(promotions.router, prefix="/api/promotions", tags=["Promotions"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

@app.get("/")
def root():
    return {"message": "B2B Tizimi ishlayapti!"}
