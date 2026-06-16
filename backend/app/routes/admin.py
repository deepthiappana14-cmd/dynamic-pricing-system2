from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PricingConfig, PricingTier
from ..schemas import (
    PricingConfigRead,
    PricingConfigUpdate,
    PricingTierCreate,
    PricingTierRead,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def get_config(db: Session) -> PricingConfig:
    config = db.query(PricingConfig).first()
    if not config:
        raise HTTPException(status_code=404, detail="Pricing configuration not found")
    return config


@router.get("/config", response_model=PricingConfigRead)
def read_config(db: Session = Depends(get_db)):
    return get_config(db)


@router.patch("/config", response_model=PricingConfigRead)
def update_config(payload: PricingConfigUpdate, db: Session = Depends(get_db)):
    config = get_config(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    db.commit()
    db.refresh(config)
    return config


@router.get("/tiers", response_model=list[PricingTierRead])
def list_tiers(db: Session = Depends(get_db)):
    config = get_config(db)
    return config.tiers


@router.post("/tiers", response_model=PricingTierRead, status_code=201)
def create_tier(payload: PricingTierCreate, db: Session = Depends(get_db)):
    config = get_config(db)
    tier = PricingTier(config_id=config.id, **payload.model_dump())
    db.add(tier)
    db.commit()
    db.refresh(tier)
    return tier


@router.put("/tiers/{tier_id}", response_model=PricingTierRead)
def update_tier(tier_id: int, payload: PricingTierCreate, db: Session = Depends(get_db)):
    tier = db.query(PricingTier).filter(PricingTier.id == tier_id).first()
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    for field, value in payload.model_dump().items():
        setattr(tier, field, value)
    db.commit()
    db.refresh(tier)
    return tier


@router.delete("/tiers/{tier_id}", status_code=204)
def delete_tier(tier_id: int, db: Session = Depends(get_db)):
    tier = db.query(PricingTier).filter(PricingTier.id == tier_id).first()
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    db.delete(tier)
    db.commit()
