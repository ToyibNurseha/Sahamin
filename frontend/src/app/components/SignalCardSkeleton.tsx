export default function SignalCardSkeleton() {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded overflow-hidden animate-pulse">
      <div className="h-0.5 bg-zinc-800" />
      <div className="p-3 space-y-2.5">
        <div className="flex justify-between">
          <div className="h-4 bg-zinc-800 rounded w-24" />
          <div className="h-4 bg-zinc-800 rounded w-16" />
        </div>
        <div className="h-3 bg-zinc-800 rounded w-32" />
        <div className="grid grid-cols-3 gap-1">
          {[0, 1, 2].map(i => (
            <div key={i} className="space-y-1">
              <div className="h-2 bg-zinc-800 rounded w-8" />
              <div className="h-4 bg-zinc-800 rounded" />
            </div>
          ))}
        </div>
        <div className="flex justify-between">
          <div className="h-3 bg-zinc-800 rounded w-16" />
          <div className="h-3 bg-zinc-800 rounded w-10" />
        </div>
      </div>
    </div>
  )
}
