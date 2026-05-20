import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import engine, Base, run_migrations
import backend.models  # noqa: F401 — registers models with Base.metadata
from backend.routers import coins, trends, alerts, auth, payment
from backend.scheduler import start_scheduler
from backend.crawler import seed_alerts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

app = FastAPI(title="CryptoHub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(coins.router)
app.include_router(trends.router)
app.include_router(alerts.router)
app.include_router(auth.router)
app.include_router(payment.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    run_migrations()
    seed_alerts()
    start_scheduler()
    logging.getLogger("main").info("CryptoHub API started")


@app.get("/")
@app.head("/", include_in_schema=False)
def root():
    return {"status": "ok", "app": "CryptoHub API"}


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
