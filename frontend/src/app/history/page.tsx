import Link from 'next/link'
import { fetchHistory } from '../lib/api'
import { formatPct, formatDate } from '../lib/format'
import Header from '../components/Header'

export default async function HistoryPage() {
  type FetchResult =
    | { ok: true; history: Awaited<ReturnType<typeof fetchHistory>> }
    | { ok: false; error: string }

  let result: FetchResult
  try {
    const history = await fetchHistory(30)
    result = { ok: true, history }
  } catch {
    result = { ok: false, error: 'Failed to connect to backend at localhost:8000 — make sure the API server is running.' }
  }

  const history = result.ok ? result.history : []
  const wins = history.filter(h => h.status === 'WIN')
  const losses = history.filter(h => h.status === 'LOSS')
  const resolved = wins.length + losses.length
  const winRate = resolved > 0 ? (wins.length / resolved) * 100 : 0
  const cumPnl = history.reduce((sum, h) => sum + (h.pct ?? 0), 0)

  return (
    <main className="min-h-screen bg-black">
      <Header />

      <div className="max-w-screen-xl mx-auto px-4 py-4 space-y-4">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-xs">
          <Link href="/" className="text-zinc-600 hover:text-zinc-400 transition-colors tracking-wider">
            ← DASHBOARD
          </Link>
          <span className="text-zinc-800">/</span>
          <span className="text-zinc-500 tracking-widest uppercase">History</span>
        </div>

        {/* Error banner */}
        {!result.ok && (
          <div className="border border-red-900 bg-red-950/20 text-red-400 text-xs px-4 py-3 rounded tracking-wide">
            {result.error}
          </div>
        )}

        {/* Summary bar */}
        {history.length > 0 && (
          <div className="bg-zinc-900 border border-zinc-800 rounded p-4 flex flex-wrap gap-x-6 gap-y-3 text-xs">
            <Stat label="Signals (30d)" value={history.length} cls="text-zinc-100" />
            <Stat label="Wins" value={wins.length} cls="text-emerald-400" />
            <Stat label="Losses" value={losses.length} cls="text-red-400" />
            <Stat
              label="Win Rate"
              value={`${winRate.toFixed(1)}%`}
              cls={winRate >= 50 ? 'text-emerald-400' : 'text-red-400'}
            />
            <Stat
              label="Cum P&L (30d)"
              value={formatPct(cumPnl)}
              cls={cumPnl >= 0 ? 'text-emerald-400' : 'text-red-400'}
            />
          </div>
        )}

        {/* Empty state */}
        {result.ok && history.length === 0 && (
          <div className="text-center py-24 text-zinc-600 text-xs tracking-widest">
            No history data available.
          </div>
        )}

        {/* Table */}
        {history.length > 0 && (
          <div className="bg-zinc-900 border border-zinc-800 rounded overflow-hidden">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-zinc-800">
                  <Th>Date</Th>
                  <Th right>Result %</Th>
                  <Th right>Status</Th>
                </tr>
              </thead>
              <tbody>
                {history.map((entry, i) => (
                  <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors">
                    <td className="px-4 py-2 text-zinc-400">{formatDate(entry.date)}</td>
                    <td className={`px-4 py-2 text-right tabular-nums font-bold ${(entry.pct ?? 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {formatPct(entry.pct)}
                    </td>
                    <td className="px-4 py-2 text-right">
                      <span className={`font-bold tracking-widest ${
                        entry.status === 'WIN'  ? 'text-emerald-400' :
                        entry.status === 'LOSS' ? 'text-red-400'     :
                        entry.status === 'OPEN' ? 'text-sky-400'     : 'text-zinc-500'
                      }`}>
                        {entry.status ?? '—'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <footer className="border-t border-zinc-900 px-4 py-4 text-center text-zinc-700 text-xs tracking-widest mt-8">
        IDX INSIGHTS — INDONESIAN STOCK EXCHANGE SIGNAL DASHBOARD
      </footer>
    </main>
  )
}

function Stat({ label, value, cls }: { label: string; value: number | string; cls: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-zinc-600 uppercase tracking-wider text-[10px]">{label}</span>
      <span className={`font-bold text-sm ${cls}`}>{value}</span>
    </div>
  )
}

function Th({ children, right }: { children: React.ReactNode; right?: boolean }) {
  return (
    <th className={`text-zinc-600 uppercase tracking-wider px-4 py-2 font-normal text-[10px] ${right ? 'text-right' : 'text-left'}`}>
      {children}
    </th>
  )
}
