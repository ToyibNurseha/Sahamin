export function formatPrice(price: number | null | undefined): string {
  if (price == null) return '—'
  return price.toLocaleString('id-ID')
}

export function formatPct(pct: number | null | undefined): string {
  if (pct == null) return '—'
  const sign = pct >= 0 ? '+' : ''
  return `${sign}${pct.toFixed(2)}%`
}

export function formatScore(score: number | null | undefined): string {
  if (score == null) return '—'
  const sign = score >= 0 ? '+' : ''
  return `${sign}${score.toFixed(1)}`
}

export function formatDate(dateStr: string): string {
  try {
    const [year, month, day] = dateStr.split('-').map(Number)
    const date = new Date(year, month - 1, day)
    return date.toLocaleDateString('id-ID', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return dateStr
  }
}

export function getTodayDate(): string {
  return new Date().toISOString().split('T')[0]
}

export function getSignalTextColor(label: string): string {
  if (label === 'STRONG BUY') return 'text-emerald-400'
  if (label === 'BUY') return 'text-green-400'
  if (label === 'HOLD') return 'text-yellow-400'
  if (label === 'SELL') return 'text-orange-400'
  if (label === 'STRONG SELL') return 'text-red-400'
  return 'text-zinc-400'
}

export function getSignalBarColor(label: string): string {
  if (label === 'STRONG BUY') return 'bg-emerald-400'
  if (label === 'BUY') return 'bg-green-400'
  if (label === 'HOLD') return 'bg-yellow-400'
  if (label === 'SELL') return 'bg-orange-400'
  if (label === 'STRONG SELL') return 'bg-red-400'
  return 'bg-zinc-600'
}

export function getResultBorderColor(status: string | null | undefined): string {
  if (status === 'WIN') return '#34d399'  // emerald-400
  if (status === 'LOSS') return '#ef4444' // red-500
  if (status === 'OPEN') return '#0ea5e9' // sky-500
  return '#3f3f46'                         // zinc-700
}

export function getResultTextColor(status: string | null | undefined): string {
  if (status === 'WIN') return 'text-emerald-400'
  if (status === 'LOSS') return 'text-red-400'
  if (status === 'OPEN') return 'text-sky-400'
  return 'text-zinc-500'
}
