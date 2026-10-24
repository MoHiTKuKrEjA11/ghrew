from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import accuracy, forecast


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Wind Forecast Monitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(forecast.router)
app.include_router(accuracy.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
