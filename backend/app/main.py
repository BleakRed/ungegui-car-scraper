import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routes.cars import router as cars_router
from .scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    if os.getenv("AUTO_SCRAPE", "true").lower() == "true":
        logger.info("Initial scrape skipped on startup — scheduler will populate DB")

    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Unegui Car Scraper API",
    description="API for scraped car listings from unegui.mn",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cars_router)


@app.get("/")
def root():
    return {"message": "Unegui Car Scraper API", "docs": "/docs"}
