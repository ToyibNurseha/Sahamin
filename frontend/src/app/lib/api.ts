export type SignalLabel = 'STRONG BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG SELL'
export type ResultStatus = 'WIN' | 'LOSS' | 'OPEN' | null

export interface IndicatorBreakdown {
  rsi?: number
  macd?: number
  ema_cross?: number
  bollinger?: number
  stochastic?: number
  adx?: number
  volume?: number
}

export interface Indicators {
  rsi?: number
  macd_hist?: number
  ema20?: number
  ema50?: number
  adx?: number
  vol_ratio?: number
  breakdown?: IndicatorBreakdown
}

export interface Signal {
  id: number
  symbol: string
  date: string
  score: number
  signal_label: SignalLabel
  trade_type: string
  entry_price: number
  target_price: number
  stop_loss: number
  risk_reward: number
  indicators?: Indicators
  result_status?: ResultStatus
  result_pct?: number | null
}

export interface Summary {
  date: string
  total: number
  strong_buy: number
  buy: number
  hold: number
  sell: number
  strong_sell: number
  wins?: number
  losses?: number
  win_rate?: number
  cum_pnl?: number
}

export interface HistoryEntry {
  date: string
  status: ResultStatus
  pct: number
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function fetchSignals(date: string, label?: string): Promise<Signal[]> {
  const params = new URLSearchParams({ date })
  if (label) params.set('label', label)
  const res = await fetch(`${BASE_URL}/signals?${params}`, { cache: 'no-store' })
  if (!res.ok) throw new Error('Failed to fetch signals')
  return res.json()
}

export async function fetchSummary(date: string): Promise<Summary> {
  const res = await fetch(`${BASE_URL}/summary?date=${date}`, { cache: 'no-store' })
  if (!res.ok) throw new Error('Failed to fetch summary')
  return res.json()
}

export async function fetchHistory(days = 30): Promise<HistoryEntry[]> {
  const res = await fetch(`${BASE_URL}/history?days=${days}`, { cache: 'no-store' })
  if (!res.ok) throw new Error('Failed to fetch history')
  return res.json()
}
