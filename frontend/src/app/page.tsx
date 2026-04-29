import { fetchSignals, fetchSummary } from './lib/api'
import { getTodayDate } from './lib/format'
import Header from './components/Header'
import SummaryBar from './components/SummaryBar'
import FilterTabs from './components/FilterTabs'
import SignalCard from './components/SignalCard'

interface PageProps {
  searchParams: { date?: string; label?: string }
}

export default async function Dashboard({ searchParams }: PageProps) {
  const date = searchParams.date || getTodayDate()
  const label = searchParams.label

  type FetchResult =
    | { ok: true; signals: Awaited<ReturnType<typeof fetchSignals>>; summary: Awaited<ReturnType<typeof fetchSummary>> }
    | { ok: false; error: string }

  let result: FetchResult
  try {
    const [signals, summary] = await Promise.all([
      fetchSignals(date, label),
      fetchSummary(date),
    ])
    result = { ok: true, signals, summary }
  } catch {
    result = { ok: false, error: 'Failed to connect to backend at localhost:8000 — make sure the API server is running.' }
  }

  const signals = result.ok ? result.signals : []
  const summary = result.ok ? result.summary : null

  // Only split HOLD into a collapsed section when showing unfiltered view
  const mainSignals = label ? signals : signals.filter(s => s.signal_label !== 'HOLD')
  const holdSignals = label ? [] : signals.filter(s => s.signal_label === 'HOLD')

  return (
    <main className="min-h-screen bg-black">
      <Header date={date} />

      <div className="max-w-screen-2xl mx-auto px-4 py-4 space-y-4">
        {/* Error banner */}
        {!result.ok && (
          <div className="border border-red-900 bg-red-950/20 text-red-400 text-xs px-4 py-3 rounded tracking-wide">
            {result.error}
          </div>
        )}

        {/* Summary stats */}
        {summary && <SummaryBar summary={summary} />}

        {/* Filter tabs */}
        <FilterTabs activeLabel={label} date={searchParams.date} />

        {/* Empty state */}
        {result.ok && signals.length === 0 && (
          <div className="text-center py-24 text-zinc-600 text-xs tracking-widest">
            No signals for {date}. Run: python scheduler.py --now
          </div>
        )}

        {/* Main signal grid */}
        {mainSignals.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {mainSignals.map((signal, i) => (
              <SignalCard key={signal.id} signal={signal} rank={i + 1} />
            ))}
          </div>
        )}

        {/* HOLD section — collapsed by default */}
        {holdSignals.length > 0 && (
          <details className="group">
            <summary className="cursor-pointer list-none select-none text-yellow-400 text-xs tracking-widest uppercase border border-yellow-900/40 bg-yellow-950/10 px-4 py-2 rounded flex items-center gap-2 hover:bg-yellow-950/20 transition-colors">
              <span className="transition-transform group-open:rotate-90 inline-block">▶</span>
              HOLD — {holdSignals.length} signals
            </summary>
            <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {holdSignals.map((signal, i) => (
                <SignalCard key={signal.id} signal={signal} rank={mainSignals.length + i + 1} />
              ))}
            </div>
          </details>
        )}
      </div>

      <footer className="border-t border-zinc-900 px-4 py-4 text-center text-zinc-700 text-xs tracking-widest mt-8">
        IDX INSIGHTS — INDONESIAN STOCK EXCHANGE SIGNAL DASHBOARD
      </footer>
    </main>
  )
}
