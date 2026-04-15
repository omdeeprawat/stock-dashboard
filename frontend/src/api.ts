import axios from "axios";
import type { Company, StockDataPoint, Summary } from "./types";


const BASE = "https://stock-dashboard-aqms.onrender.com/api";

export const fetchCompanies = () =>
  axios.get<Company[]>(`${BASE}/companies`).then((r) => r.data);

export const fetchStockData = (symbol: string, days: number) =>
  axios.get<StockDataPoint[]>(`${BASE}/data/${symbol}?days=${days}`).then((r) => r.data);

export const fetchSummary = (symbol: string) =>
  axios.get<Summary>(`${BASE}/summary/${symbol}`).then((r) => r.data);

export const fetchCompare = (symbol1: string, symbol2: string, days: number) =>
  axios
    .get(`${BASE}/compare?symbol1=${symbol1}&symbol2=${symbol2}&days=${days}`)
    .then((r) => r.data);