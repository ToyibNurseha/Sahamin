import { Summary } from '../lib/api'
import { formatPct } from '../lib/format'

interface SummaryBarProps {
  summary: Summary
}

export default function SummaryBar({ summary }: SummaryBarProps) {
  const hasResults = summary.wins != null

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded p-4 flex flex-wrap gap-x-6 gap-y-3 items-center text-xs">
      <Stat label="Analyzed" value={summary.total} valueClass="text-zinc-100" />
      <Stat label="Strong Buy" value={summary.strong_buy} valueClass="text-emerald-400" />
      <Stat label="Buy" value={summary.buy} valueClass="text-green-400" />
      <Stat label="Hold" value={summary.hold} valueClass="text-yellow-400" />
      <Stat label="Sell" value={summary.sell} valueClass="text-orange-400" />
      <Stat label="Strong Sell" value={summary.strong_sell} valueClass="text-red-400" />

      {hasResults && (
        <>
          <div className="w-px h-8 bg-zinc-700 hidden sm:block" />
          <Stat label="Wins" value={summary.wins!} valueClass="text-emerald-400" />
          <Stat label="Losses" value={summary.losses!} valueClass="text-red-400" />
          <Stat
            label="Win Rate"
            value={`${summary.win_rate?.toFixed(1)}%`}
            valueClass={(summary.win_rate ?? 0) >= 50 ? 'text-emerald-400' : 'text-red-400'}
          />
          <Stat
            label="Cum P&L"
            value={formatPct(summary.cum_pnl)}
            valueClass={(summary.cum_pnl ?? 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}
          />
        </>
      )}
    </div>
  )
}

function Stat({ label, value, valueClass }: { label: string; value: number | string; valueClass: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-zinc-600 uppercase tracking-wider text-[10px]">{label}</span>
      <span className={`font-bold text-sm ${valueClass}`}>{value}</span>
    </div>
  )
}
