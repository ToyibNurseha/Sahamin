'use client'

import { useState } from 'react'
import type { IndicatorBreakdown as IBreakdown, Indicators } from '../lib/api'

interface Props {
  breakdown: IBreakdown
  indicators?: Indicators
}

const ROWS: [keyof IBreakdown, string][] = [
  ['rsi',        'RSI'],
  ['macd',       'MACD'],
  ['ema_cross',  'EMA CROSS'],
  ['bollinger',  'BOLLINGER'],
  ['stochastic', 'STOCH'],
  ['adx',        'ADX'],
  ['volume',     'VOLUME'],
]

export default function IndicatorBreakdown({ breakdown, indicators }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <div className="mt-2 border-t border-zinc-800 pt-2">
      <button
        onClick={() => setOpen(!open)}
        className="text-[10px] text-zinc-600 hover:text-zinc-400 transition-colors tracking-widest uppercase flex items-center gap-1"
      >
        INDICATORS {open ? '▲' : '▼'}
      </button>

      {open && (
        <div className="mt-2 space-y-2">
          {/* Raw values */}
          {indicators && (
            <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-[10px] mb-2">
              {indicators.rsi != null && <RawRow k="RSI" v={indicators.rsi.toFixed(1)} />}
              {indicators.macd_hist != null && <RawRow k="MACD HIST" v={indicators.macd_hist.toFixed(2)} />}
              {indicators.adx != null && <RawRow k="ADX" v={indicators.adx.toFixed(1)} />}
              {indicators.vol_ratio != null && <RawRow k="VOL RATIO" v={`${indicators.vol_ratio.toFixed(2)}×`} />}
              {indicators.ema20 != null && indicators.ema50 != null && (
                <RawRow k="EMA 20/50" v={`${indicators.ema20.toLocaleString('id-ID')} / ${indicators.ema50.toLocaleString('id-ID')}`} />
              )}
            </div>
          )}

          {/* Vote bars */}
          <div className="text-[10px] text-zinc-600 uppercase tracking-widest mb-1">VOTES</div>
          {ROWS.map(([key, name]) => {
            const val = breakdown[key]
            if (val == null) return null
            const width = Math.min((Math.abs(val) / 2) * 100, 100)
            const positive = val >= 0

            return (
              <div key={key} className="flex items-center gap-2 text-[10px]">
                <span className="text-zinc-500 w-[72px] shrink-0">{name}</span>
                <div className="flex-1 h-1 bg-zinc-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${positive ? 'bg-emerald-400' : 'bg-red-400'}`}
                    style={{ width: `${width}%` }}
                  />
                </div>
                <span className={`w-7 text-right tabular-nums ${positive ? 'text-emerald-400' : 'text-red-400'}`}>
                  {positive ? '+' : ''}{val}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function RawRow({ k, v }: { k: string; v: string }) {
  return (
    <>
      <span className="text-zinc-600">{k}</span>
      <span className="text-zinc-400">{v}</span>
    </>
  )
}
