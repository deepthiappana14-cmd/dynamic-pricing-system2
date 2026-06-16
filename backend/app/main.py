from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, SessionLocal, engine
from .models import PricingConfig, PricingTier
from .routes import admin, pricing, users


def seed_database() -> None:
    db = SessionLocal()
    try:
        if db.query(PricingConfig).first():
            return

        config = PricingConfig(
            mode="tiered",
            base_price=9.99,
            per_user_rate=0.05,
            currency="USD",
        )
        db.add(config)
        db.flush()

        default_tiers = [
            PricingTier(
                config_id=config.id,
                min_users=0,
                max_users=50,
                price=9.99,
                label="Starter (0–50 users)",
            ),
            PricingTier(
                config_id=config.id,
                min_users=51,
                max_users=200,
                price=19.99,
                label="Growth (51–200 users)",
            ),
            PricingTier(
                config_id=config.id,
                min_users=201,
                max_users=500,
                price=34.99,
                label="Scale (201–500 users)",
            ),
            PricingTier(
                config_id=config.id,
                min_users=501,
                max_users=None,
                price=59.99,
                label="Enterprise (501+ users)",
            ),
        ]
        db.add_all(default_tiers)
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(
    title="Dynamic Pricing API",
    description="Adjusts service prices based on active user count",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://dynamic-pricing-system2.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api")
app.include_router(pricing.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


STATIC_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"

if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/")
    def serve_frontend():
        return FileResponse(STATIC_DIR / "index.html")
