import Link from 'next/link'

interface FilterTabsProps {
  activeLabel?: string
  date?: string
}

const FILTERS = [
  { label: 'ALL',         value: '',            textClass: 'text-zinc-400',    borderClass: 'border-zinc-700' },
  { label: 'STRONG BUY', value: 'STRONG BUY',  textClass: 'text-emerald-400', borderClass: 'border-emerald-800' },
  { label: 'BUY',        value: 'BUY',          textClass: 'text-green-400',   borderClass: 'border-green-800' },
  { label: 'HOLD',       value: 'HOLD',         textClass: 'text-yellow-400',  borderClass: 'border-yellow-800' },
  { label: 'SELL',       value: 'SELL',         textClass: 'text-orange-400',  borderClass: 'border-orange-800' },
  { label: 'STRONG SELL',value: 'STRONG SELL',  textClass: 'text-red-400',     borderClass: 'border-red-800' },
]

export default function FilterTabs({ activeLabel, date }: FilterTabsProps) {
  const dateQuery = date ? `date=${date}&` : ''

  return (
    <div className="flex flex-wrap gap-2">
      {FILTERS.map(({ label, value, textClass, borderClass }) => {
        const isActive = value === '' ? !activeLabel : value === activeLabel
        const href = value
          ? `/?${dateQuery}label=${encodeURIComponent(value)}`
          : date ? `/?date=${date}` : '/'

        return (
          <Link
            key={label}
            href={href}
            className={`
              text-xs px-3 py-1 border rounded-full tracking-wider uppercase transition-all
              ${textClass} ${borderClass}
              ${isActive ? 'opacity-100' : 'opacity-40 hover:opacity-70'}
            `}
          >
            {label}
          </Link>
        )
      })}
    </div>
  )
}
