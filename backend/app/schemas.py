from pydantic import BaseModel
from datetime import date
from typing import Optional

class CompanyOut(BaseModel):
  symbol: str
  name: str
  sector: Optional[str] = None

  model_config = {"from_attributes": True}


class StockDataOut(BaseModel):
  date: date
  open: float
  high: float
  low: float
  close: float
  volume: float
  daily_return: Optional[float] = None
  ma_7: Optional[float] = None

  model_config = {"from_attributes": True}


class SummaryOut(BaseModel):
  symbol: str
  high_52w: float
  low_52w: float
  avg_close: float
  volatility_score: float  