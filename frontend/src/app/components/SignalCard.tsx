import type { Signal } from '../lib/api'
import {
  formatPrice, formatPct, formatScore,
  getSignalTextColor, getSignalBarColor,
  getResultBorderColor, getResultTextColor,
} from '../lib/format'
import IndicatorBreakdown from './IndicatorBreakdown'

interface SignalCardProps {
  signal: Signal
  rank: number
}

export default function SignalCard({ signal, rank }: SignalCardProps) {
  const scoreBarWidth = Math.min((Math.abs(signal.score) / 10) * 100, 100)
  const barColor = getSignalBarColor(signal.signal_label)
  const borderLeftColor = getResultBorderColor(signal.result_status)
  const hasResult = signal.result_status != null

  return (
    <div
      className="bg-zinc-900 border border-zinc-800 rounded overflow-hidden hover:border-zinc-600 transition-colors"
      style={{ borderLeftColor, borderLeftWidth: '2px' }}
    >
      {/* Score progress bar */}
      <div className="h-0.5 w-full bg-zinc-800">
        <div className={`h-full ${barColor}`} style={{ width: `${scoreBarWidth}%` }} />
      </div>

      <div className="p-3 space-y-2.5">
        {/* Row 1: rank + symbol | result % or signal badge */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-1.5">
            <span className="text-zinc-600 text-xs tabular-nums">#{rank}</span>
            <span className="text-zinc-100 font-bold tracking-widest text-sm uppercase">{signal.symbol}</span>
          </div>
          {hasResult ? (
            <span className={`text-xs font-bold tabular-nums ${(signal.result_pct ?? 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {formatPct(signal.result_pct)}
            </span>
          ) : (
            <span className={`text-[10px] border px-1.5 py-0.5 rounded-full tracking-wider shrink-0 ${getSignalTextColor(signal.signal_label)} border-current opacity-70`}>
              {signal.signal_label}
            </span>
          )}
        </div>

        {/* Row 2: trade type | score */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-sky-400 tracking-wider uppercase">{signal.trade_type}</span>
          <span className="text-zinc-700">|</span>
          <span className={signal.score >= 0 ? 'text-emerald-400' : 'text-red-400'}>
            SCORE {formatScore(signal.score)}
          </span>
        </div>

        {/* Row 3: Entry / Target / Stop */}
        <div className="grid grid-cols-3 gap-1 text-xs">
          <div className="space-y-0.5">
            <div className="text-zinc-600 uppercase tracking-wider text-[10px]">Entry</div>
            <div className="text-zinc-100 tabular-nums">{formatPrice(signal.entry_price)}</div>
          </div>
          <div className="space-y-0.5">
            <div className="text-zinc-600 uppercase tracking-wider text-[10px]">Target</div>
            <div className="text-emerald-400 tabular-nums">{formatPrice(signal.target_price)}</div>
          </div>
          <div className="space-y-0.5">
            <div className="text-zinc-600 uppercase tracking-wider text-[10px]">Stop</div>
            <div className="text-red-400 tabular-nums">{formatPrice(signal.stop_loss)}</div>
          </div>
        </div>

        {/* Row 4: R/R | result status */}
        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-400 tabular-nums">R/R {signal.risk_reward?.toFixed(1)}:1</span>
          {hasResult && (
            <span className={`font-bold tracking-widest text-[10px] ${getResultTextColor(signal.result_status)}`}>
              {signal.result_status}
            </span>
          )}
        </div>

        {/* Indicator breakdown — client component */}
        {signal.indicators?.breakdown && (
          <IndicatorBreakdown
            breakdown={signal.indicators.breakdown}
            indicators={signal.indicators}
          />
        )}
      </div>
    </div>
  )
}
