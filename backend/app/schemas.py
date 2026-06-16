from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PricingTierBase(BaseModel):
    min_users: int = Field(ge=0)
    max_users: int | None = Field(default=None, ge=0)
    price: float = Field(gt=0)
    label: str = ""


class PricingTierCreate(PricingTierBase):
    pass


class PricingTierRead(PricingTierBase):
    id: int

    model_config = {"from_attributes": True}


class PricingConfigUpdate(BaseModel):
    mode: Literal["tiered", "linear"] | None = None
    base_price: float | None = Field(default=None, gt=0)
    per_user_rate: float | None = Field(default=None, ge=0)
    currency: str | None = None


class PricingConfigRead(BaseModel):
    id: int
    mode: str
    base_price: float
    per_user_rate: float
    currency: str
    updated_at: datetime
    tiers: list[PricingTierRead]

    model_config = {"from_attributes": True}


class PriceQuote(BaseModel):
    active_users: int
    mode: str
    price: float
    currency: str
    breakdown: str
    tier_label: str | None = None


class ActiveUserCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)


class ActiveUserRead(BaseModel):
    id: int
    session_id: str
    display_name: str
    is_active: bool
    joined_at: datetime
    last_seen_at: datetime

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    active_users: int
    total_users: int
    current_price: PriceQuote
    config: PricingConfigRead
