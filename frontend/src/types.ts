export interface Company {
  symbol: string;
  name: string;
  sector: string | null;
}

export interface StockDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  daily_return: number | null;
  ma_7: number | null;
}

export interface Summary {
  symbol: string;
  high_52w: number;
  low_52w: number;
  avg_close: number;
  volatility_score: number;
}

export type TimeRange = 30 | 90 | 180 | 365;