import RankingRow from '../../components/voting/RankingRow'

const filterChips = [
  { label: '全部', count: 12, active: true },
  { label: '景點', count: 7 },
  { label: '餐廳', count: 5 },
]

const rankings = [
  {
    rank: 1,
    title: '伏見稻荷大社',
    category: '景點' as const,
    proposedBy: 'Sophie',
    votes: 4,
    voted: true,
  },
  {
    rank: 2,
    title: '嵐山竹林小徑',
    category: '景點' as const,
    proposedBy: 'Jordan',
    votes: 3,
    voted: true,
  },
  {
    rank: 3,
    title: '一蘭拉麵 — 澀谷',
    category: '餐廳' as const,
    proposedBy: 'Alex',
    votes: 3,
    voted: false,
  },
  {
    rank: 4,
    title: '金閣寺',
    category: '景點' as const,
    proposedBy: 'Riley',
    votes: 2,
    voted: false,
  },
]

export default function TripVotingPage() {
  return (
    <div className="p-6 max-w-5xl">
      {/* Header */}
      <div className="mb-6">
        <h2 className="font-display text-xl font-semibold text-ink">群組投票</h2>
        <p className="text-sm text-muted mt-1">12 個地點 · 依票數排序</p>
      </div>

      {/* Filter chips */}
      <div className="flex items-center gap-2 flex-wrap mb-6">
        {filterChips.map(({ label, count, active }) => (
          <button
            key={label}
            type="button"
            className={[
              'inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm transition-colors',
              active
                ? 'bg-ink text-brand-fg font-medium'
                : 'bg-surface border border-line text-muted hover:bg-brand-soft hover:text-ink',
            ].join(' ')}
          >
            {label}
            <span className="text-xs opacity-70">{count}</span>
          </button>
        ))}
      </div>

      {/* Ranked list */}
      <div className="flex flex-col gap-3">
        {rankings.map((row) => (
          <RankingRow key={row.title} {...row} />
        ))}
      </div>
    </div>
  )
}
