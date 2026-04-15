from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Company, StockData
from app.schemas import CompanyOut, StockDataOut, SummaryOut
from app.services.analytics import get_last_n_days, get_summary, compare_stocks
from app.cache import get_cache, set_cache
import json
from app.services.cache import get_redis


router = APIRouter()


@router.get("/companies", response_model=list[CompanyOut])
async def list_companies(db: AsyncSession = Depends(get_db)):
    cached = await get_cache("companies")
    if cached:
        return json.loads(cached)

    result = await db.execute(select(Company).order_by(Company.symbol))
    companies = result.scalars().all()

    data = [CompanyOut.model_validate(c).model_dump() for c in companies]
    await set_cache("companies", json.dumps(data), ttl=3600)
    return data


@router.get("/data/{symbol}", response_model=list[StockDataOut])
async def get_stock_data(
    symbol: str,
    days: int = Query(default=30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"data:{symbol}:{days}"
    cached = await get_cache(cache_key)
    if cached:
        return json.loads(cached)

    # Validate symbol exists
    result = await db.execute(select(Company).where(Company.symbol == symbol))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")

    records = await get_last_n_days(db, symbol, days)
    if not records:
        raise HTTPException(status_code=404, detail="No data found for this symbol")

    data = [StockDataOut.model_validate(r).model_dump(mode="json") for r in records]
    await set_cache(cache_key, json.dumps(data), ttl=3600)
    return data


@router.get("/summary/{symbol}", response_model=SummaryOut)
async def get_stock_summary(symbol: str, db: AsyncSession = Depends(get_db)):
    cache_key = f"summary:{symbol}"
    cached = await get_cache(cache_key)
    if cached:
        return json.loads(cached)

    result = await db.execute(select(Company).where(Company.symbol == symbol))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")

    summary = await get_summary(db, symbol)
    await set_cache(cache_key, json.dumps(summary), ttl=3600)
    return summary


@router.get("/compare")
async def compare(
    symbol1: str = Query(...),
    symbol2: str = Query(...),
    days: int = Query(default=30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"compare:{symbol1}:{symbol2}:{days}"
    cached = await get_cache(cache_key)
    if cached:
      return json.loads(cached)

    # Validate both symbols
    for sym in [symbol1, symbol2]:
      result = await db.execute(select(Company).where(Company.symbol == sym))
      if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Symbol '{sym}' not found")

    data = await compare_stocks(db, symbol1, symbol2, days)
    await set_cache(cache_key, json.dumps(data), ttl=3600)
    return data


@router.get("/cache/flush")
async def flush_cache():
    r = await get_redis()
    await r.flushall()
    return {"status": "cache flushed"}