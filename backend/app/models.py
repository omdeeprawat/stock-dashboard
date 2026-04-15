from sqlalchemy import Column, String, Float, Date, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Company(Base):
  __tablename__ = "companies"

  id = Column(Integer, primary_key=True, index=True)
  symbol = Column(String, unique=True, index=True, nullable=False)
  name = Column(String, nullable=False)
  sector = Column(String, nullable=True)

  stock_data = relationship("StockData", back_populates="company", cascade="all, delete")


class StockData(Base):
  __tablename__ = "stock_data"

  id = Column(Integer, primary_key=True, index=True)
  symbol = Column(String, ForeignKey("companies.symbol", ondelete="CASCADE"), nullable=False)
  date = Column(Date, nullable=False)
  open = Column(Float)
  high = Column(Float)
  low = Column(Float)
  close = Column(Float)
  volume = Column(Float)

  # Computed metrics (stored for fast retrieval)
  daily_return = Column(Float, nullable=True)
  ma_7 = Column(Float, nullable=True)

  company = relationship("Company", back_populates="stock_data")

  __table_args__ = (
    UniqueConstraint("symbol", "date", name="uq_symbol_date"),
  )