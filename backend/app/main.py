import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import check_database_connection, get_db

logger = logging.getLogger("medsync")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if check_database_connection():
        logger.info("Database connection verified on startup.")
    else:
        logger.warning("Could not connect to the database on startup.")
    yield


app = FastAPI(title="MedSync API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except OperationalError as exc:
        raise HTTPException(status_code=503, detail="database unreachable") from exc
    return {"status": "ok", "database": "connected"}
