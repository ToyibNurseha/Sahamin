import Header from './components/Header'
import SignalCardSkeleton from './components/SignalCardSkeleton'

export default function Loading() {
  return (
    <main className="min-h-screen bg-black">
      <Header />
      <div className="max-w-screen-2xl mx-auto px-4 py-4 space-y-4">
        {/* Summary skeleton */}
        <div className="bg-zinc-900 border border-zinc-800 rounded p-4 flex gap-6 animate-pulse">
          {[0, 1, 2, 3, 4, 5].map(i => (
            <div key={i} className="space-y-1">
              <div className="h-2 bg-zinc-800 rounded w-16" />
              <div className="h-4 bg-zinc-800 rounded w-8" />
            </div>
          ))}
        </div>
        {/* Filter tabs skeleton */}
        <div className="flex gap-2 animate-pulse">
          {[0, 1, 2, 3, 4, 5].map(i => (
            <div key={i} className="h-6 bg-zinc-800 rounded-full w-20" />
          ))}
        </div>
        {/* Cards grid skeleton */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {Array.from({ length: 12 }).map((_, i) => (
            <SignalCardSkeleton key={i} />
          ))}
        </div>
      </div>
    </main>
  )
}
