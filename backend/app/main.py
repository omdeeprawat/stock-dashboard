from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import stocks

@asynccontextmanager
async def lifespan(app: FastAPI):
  # Create tables on startup
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  yield

app = FastAPI(
  title="Stock Data Intelligence Dashboard",
  version="1.0.0",
  lifespan=lifespan
)

app.include_router(stocks.router, prefix="/api", tags=["Stocks"])