import { Link, useParams } from 'react-router-dom'
import Badge from '../../components/common/Badge'
import Card from '../../components/common/Card'
import SummaryStatCard from '../../components/trip/SummaryStatCard'

const metrics = [
  { label: '提案地點數', value: 12 },
  { label: '總投票數', value: 34 },
  { label: '參與成員數', value: 4 },
  { label: '已規劃天數', value: 5 },
]

const topPlaces = [
  { rank: 1, name: '伏見稻荷大社', category: '景點', votes: 4 },
  { rank: 2, name: '嵐山竹林小徑', category: '景點', votes: 3 },
  { rank: 3, name: '一蘭拉麵 — 澀谷', category: '餐廳', votes: 3 },
  { rank: 4, name: '錦市場', category: '餐廳', votes: 2 },
]

export default function TripOverviewPage() {
  const { tripId } = useParams<{ tripId: string }>()

  return (
    <div className="p-6 max-w-5xl">
      {/* Page title */}
      <div className="mb-8">
        <h2 className="font-display text-xl font-semibold text-ink">旅程概覽</h2>
        <p className="text-sm text-muted mt-1">目前規劃狀態一覽</p>
      </div>

      {/* Metric cards — 2-col on mobile, 4-col on lg */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {metrics.map((m) => (
          <SummaryStatCard key={m.label} label={m.label} value={m.value} />
        ))}
      </div>

      {/* Two-column: top voted (wider) + quick actions (narrower) */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_220px] gap-5">
        {/* Top voted places */}
        <Card className="overflow-hidden">
          <div className="px-5 py-4 border-b border-line flex items-center justify-between">
            <h3 className="text-base font-semibold text-ink">熱門提案地點</h3>
            <Link
              to={`/trips/${tripId}/voting`}
              className="text-sm text-muted hover:text-ink transition-colors"
            >
              查看全部
            </Link>
          </div>
          <div className="p-5 flex flex-col gap-2.5">
            {topPlaces.map((place) => (
              <div
                key={place.name}
                className="flex items-center gap-3 px-4 py-3 bg-surface-soft rounded-xl"
              >
                <span className="text-sm font-bold text-muted w-5 text-center shrink-0">
                  {place.rank}
                </span>
                <span className="flex-1 text-sm font-medium text-ink min-w-0 truncate">
                  {place.name}
                </span>
                <Badge variant="neutral">{place.category}</Badge>
                <div className="flex items-center gap-1 shrink-0">
                  <span className="text-sm font-semibold text-ink">{place.votes}</span>
                  <span className="text-sm text-muted">票</span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Quick actions */}
        <Card className="p-5 flex flex-col gap-2.5">
          <h3 className="text-base font-semibold text-ink mb-1">快速操作</h3>
          <Link
            to={`/trips/${tripId}/places`}
            className="flex items-center justify-between px-4 py-3 rounded-xl border border-line text-sm text-ink hover:bg-brand-soft transition-colors"
          >
            <span>新增地點</span>
            <span className="text-muted text-sm">→</span>
          </Link>
          <Link
            to={`/trips/${tripId}/voting`}
            className="flex items-center justify-between px-4 py-3 rounded-xl border border-line text-sm text-ink hover:bg-brand-soft transition-colors"
          >
            <span>前往投票</span>
            <span className="text-muted text-sm">→</span>
          </Link>
          <Link
            to={`/trips/${tripId}/itinerary`}
            className="flex items-center justify-between px-4 py-3 rounded-xl bg-ink text-brand-fg text-sm font-medium hover:opacity-90 transition-opacity"
          >
            <span>產生行程表</span>
            <span className="text-brand-fg/70 text-sm">→</span>
          </Link>
        </Card>
      </div>
    </div>
  )
}
