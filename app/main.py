from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import Base, engine
from .routers import auth, items


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)  # use Alembic migrations in real production
    yield


app = FastAPI(title="Items API", version="2.0.0", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(items.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
