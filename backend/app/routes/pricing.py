from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PricingConfig
from ..pricing import calculate_price
from ..schemas import DashboardStats, PriceQuote, PricingConfigRead

router = APIRouter(tags=["pricing"])


@router.get("/price", response_model=PriceQuote)
def get_current_price(db: Session = Depends(get_db)):
    config = db.query(PricingConfig).first()
    if not config:
        raise HTTPException(status_code=404, detail="Pricing configuration not found")
    return calculate_price(db, config)


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    from ..models import ActiveUser

    config = db.query(PricingConfig).first()
    if not config:
        raise HTTPException(status_code=404, detail="Pricing configuration not found")

    active = db.query(ActiveUser).filter(ActiveUser.is_active.is_(True)).count()
    total = db.query(ActiveUser).count()

    return {
        "active_users": active,
        "total_users": total,
        "current_price": calculate_price(db, config),
        "config": config,
    }
