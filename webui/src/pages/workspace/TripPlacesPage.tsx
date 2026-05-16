import Button from '../../components/common/Button'
import CandidatePlaceCard from '../../components/places/CandidatePlaceCard'

const filterChips = [
  { label: '全部', count: 12, active: true },
  { label: '景點', count: 7 },
  { label: '餐廳', count: 5 },
]

const places = [
  {
    category: '景點' as const,
    title: '伏見稻荷大社',
    description: '京都著名神社，朱紅色千本鳥居綿延山頭，是京都最具代表性的景點。',
    proposedBy: 'Sophie',
    votes: 4,
    voted: true,
  },
  {
    category: '餐廳' as const,
    title: '一蘭拉麵 — 澀谷',
    description: '個人隔間式拉麵體驗，濃郁豚骨湯頭，可自選辣度與麵條軟硬。',
    proposedBy: 'Alex',
    votes: 3,
    voted: false,
  },
  {
    category: '景點' as const,
    title: '嵐山竹林小徑',
    description: '清晨薄霧中漫步高聳竹林，靜謐而壯觀，建議早晨前往人少時段。',
    proposedBy: 'Jordan',
    votes: 3,
    voted: true,
  },
  {
    category: '餐廳' as const,
    title: '京都五行拉麵',
    description: '焦がし味噌拉麵，獨特焦香味道，人氣排隊名店，務必提早到場。',
    proposedBy: 'Riley',
    votes: 1,
    voted: false,
  },
]

export default function TripPlacesPage() {
  return (
    <div className="p-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-5">
        <div>
          <h2 className="font-display text-xl font-semibold text-ink">想去的地點</h2>
          <p className="text-sm text-muted mt-1">12 個提案 · 4 位成員參與</p>
        </div>
        <Button className="shrink-0">新增地點</Button>
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

      {/* Place cards */}
      <div className="flex flex-col gap-4">
        {places.map((place) => (
          <CandidatePlaceCard key={place.title} {...place} />
        ))}
      </div>
    </div>
  )
}
