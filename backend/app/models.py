from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PricingConfig(Base):
    __tablename__ = "pricing_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mode: Mapped[str] = mapped_column(String(20), default="tiered")
    base_price: Mapped[float] = mapped_column(Float, default=9.99)
    per_user_rate: Mapped[float] = mapped_column(Float, default=0.05)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    tiers: Mapped[list["PricingTier"]] = relationship(
        back_populates="config",
        cascade="all, delete-orphan",
        order_by="PricingTier.min_users",
    )


class PricingTier(Base):
    __tablename__ = "pricing_tiers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    config_id: Mapped[int] = mapped_column(ForeignKey("pricing_config.id"))
    min_users: Mapped[int] = mapped_column(Integer, default=0)
    max_users: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price: Mapped[float] = mapped_column(Float)
    label: Mapped[str] = mapped_column(String(100), default="")

    config: Mapped["PricingConfig"] = relationship(back_populates="tiers")


class ActiveUser(Base):
    __tablename__ = "active_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
