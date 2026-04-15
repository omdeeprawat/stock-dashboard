from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import StockData
from datetime import date, timedelta
import math

async def get_last_n_days(session: AsyncSession, symbol: str, days: int = 30) -> list[StockData]:
  cutoff = date.today() - timedelta(days=days)
  result = await session.execute(
    select(StockData)
    .where(StockData.symbol == symbol, StockData.date >= cutoff)
    .order_by(StockData.date.asc())
  )
  return result.scalars().all()


async def get_summary(session: AsyncSession, symbol: str) -> dict:
  # 52-week window
  cutoff = date.today() - timedelta(weeks=52)

  result = await session.execute(
    select(
      func.max(StockData.high).label("high_52w"),
      func.min(StockData.low).label("low_52w"),
      func.avg(StockData.close).label("avg_close"),
    )
    .where(StockData.symbol == symbol, StockData.date >= cutoff)
  )
  row = result.one()

  # volatility score 
  returns_result = await session.execute(
    select(StockData.daily_return)
    .where(StockData.symbol == symbol, StockData.date >= cutoff)
    .where(StockData.daily_return.isnot(None))
  )
  returns = [r[0] for r in returns_result.fetchall()]

  if len(returns) > 1:
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    volatility = math.sqrt(variance) * math.sqrt(252)  # annualized
  else:
    volatility = 0.0

  return {
    "symbol": symbol,
    "high_52w": round(row.high_52w, 2),
    "low_52w": round(row.low_52w, 2),
    "avg_close": round(row.avg_close, 2),
    "volatility_score": round(volatility, 4),
  }


async def compare_stocks(session: AsyncSession, symbol1: str, symbol2: str, days: int = 30) -> dict:
  data1 = await get_last_n_days(session, symbol1, days)
  data2 = await get_last_n_days(session, symbol2, days)

  def to_series(records):
    return {str(r.date): {"close": r.close, "daily_return": r.daily_return} for r in records}

  return {
    symbol1: to_series(data1),
    symbol2: to_series(data2),
  }