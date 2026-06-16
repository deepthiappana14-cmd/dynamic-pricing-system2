from sqlalchemy.orm import Session

from .models import PricingConfig, PricingTier


def count_active_users(db: Session) -> int:
    from .models import ActiveUser

    return db.query(ActiveUser).filter(ActiveUser.is_active.is_(True)).count()


def calculate_tiered_price(config: PricingConfig, active_users: int) -> tuple[float, str, str | None]:
    tiers = sorted(config.tiers, key=lambda t: t.min_users)
    if not tiers:
        return config.base_price, f"No tiers configured; using base price ${config.base_price:.2f}", None

    for tier in tiers:
        upper = tier.max_users if tier.max_users is not None else float("inf")
        if tier.min_users <= active_users <= upper:
            label = tier.label or f"{tier.min_users}–{tier.max_users or '∞'} users"
            breakdown = (
                f"Tiered: {active_users} active users fall in '{label}' "
                f"→ ${tier.price:.2f}/{config.currency}"
            )
            return tier.price, breakdown, label

    last = tiers[-1]
    label = last.label or f"{last.min_users}+ users"
    breakdown = f"Above all tiers; using top tier '{label}' → ${last.price:.2f}"
    return last.price, breakdown, label


def calculate_linear_price(config: PricingConfig, active_users: int) -> tuple[float, str, None]:
    price = config.base_price + (active_users * config.per_user_rate)
    breakdown = (
        f"Linear: ${config.base_price:.2f} base + "
        f"({active_users} × ${config.per_user_rate:.2f}) = ${price:.2f}/{config.currency}"
    )
    return round(price, 2), breakdown, None


def calculate_price(db: Session, config: PricingConfig | None = None) -> dict:
    if config is None:
        config = db.query(PricingConfig).first()
    if config is None:
        raise ValueError("Pricing configuration not found")

    active_users = count_active_users(db)

    if config.mode == "linear":
        price, breakdown, tier_label = calculate_linear_price(config, active_users)
    else:
        price, breakdown, tier_label = calculate_tiered_price(config, active_users)

    return {
        "active_users": active_users,
        "mode": config.mode,
        "price": round(price, 2),
        "currency": config.currency,
        "breakdown": breakdown,
        "tier_label": tier_label,
    }
