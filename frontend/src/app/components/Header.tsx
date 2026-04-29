import Link from 'next/link'
import { formatDate, getTodayDate } from '../lib/format'

interface HeaderProps {
  date?: string
}

export default function Header({ date }: HeaderProps) {
  const displayDate = date || getTodayDate()

  return (
    <header className="border-b border-zinc-800 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400" />
        </span>
        <Link href="/" className="flex items-center gap-2">
          <span className="text-zinc-100 font-bold tracking-widest uppercase text-sm">IDX Insights</span>
          <span className="text-zinc-600 text-xs border border-zinc-800 px-1.5 py-0.5 rounded">v1.0</span>
        </Link>
        <Link href="/history" className="text-zinc-600 hover:text-zinc-400 text-xs tracking-wider transition-colors">
          HISTORY
        </Link>
      </div>
      <div className="flex flex-col items-end gap-0.5">
        <span className="text-zinc-400 text-xs">{formatDate(displayDate)}</span>
        <span className="text-zinc-600 text-xs">Next run: 07:00 WIB</span>
      </div>
    </header>
  )
}
