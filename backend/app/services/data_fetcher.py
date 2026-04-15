import yfinance as yf
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Company, StockData
from app.database import AsyncSessionLocal
import asyncio

STOCKS = {
  "INFY.NS":    ("Infosys",             "IT"),
  "TCS.NS":     ("Tata Consultancy",    "IT"),
  "RELIANCE.NS":("Reliance Industries", "Energy"),
  "HDFCBANK.NS":("HDFC Bank",           "Finance"),
  "WIPRO.NS":   ("Wipro",               "IT"),
}

def fetch_stock_df(symbol: str, period: str = "1y") -> pd.DataFrame:
  ticker = yf.Ticker(symbol)
  df = ticker.history(period=period)
  df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
  df.columns = ["open", "high", "low", "close", "volume"]
  df.index = pd.to_datetime(df.index).date  
  df.dropna(inplace=True)

  # Compute metrics
  df["daily_return"] = (df["close"] - df["open"]) / df["open"]
  df["ma_7"] = df["close"].rolling(window=7).mean()

  return df


async def seed_database():
  async with AsyncSessionLocal() as session:
    for symbol, (name, sector) in STOCKS.items():
      result = await session.execute(select(Company).where(Company.symbol == symbol))
      company = result.scalar_one_or_none()
      if not company:
        company = Company(symbol=symbol, name=name, sector=sector)
        session.add(company)

      # Fetch and insert stock data
      df = fetch_stock_df(symbol)
      for date_val, row in df.iterrows():
        exists = await session.execute(
          select(StockData).where(
            StockData.symbol == symbol,
            StockData.date == date_val
          )
        )
        if exists.scalar_one_or_none():
          continue

        record = StockData(
          symbol=symbol,
          date=date_val,
          open=row["open"],
          high=row["high"],
          low=row["low"],
          close=row["close"],
          volume=row["volume"],
          daily_return=row["daily_return"] if pd.notna(row["daily_return"]) else None,
          ma_7=row["ma_7"] if pd.notna(row["ma_7"]) else None,
      )
        session.add(record)

    await session.commit()
    print(f"✅ Seeded {symbol}")


if __name__ == "__main__":
  asyncio.run(seed_database())