from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import stocks
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from app.database import engine, Base
from app.services.data_fetcher import seed_database

from sqlalchemy import select, func
from app.models import Company
from app.database import AsyncSessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):
  # Create tables on startup
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

    # seeding
    async with AsyncSessionLocal() as session:
      result = await session.execute(select(func.count()).select_from(Company))
      count = result.scalar()
      if count == 0:
        print("🌱 DB is empty, seeding...")
        await seed_database()
        print("✅ Seeding complete")
      else:
        print(f"✅ DB already has {count} companies, skipping seed")
    yield

app = FastAPI(
  title="Stock Data Intelligence Dashboard",
  version="1.0.0",
  lifespan=lifespan
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["https://stock-dashboard.front.onrender.com"],
  allow_methods=["GET"],
  allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/api", tags=["Stocks"])