import { useEffect, useState } from 'react'
import { Link, useOutletContext, useParams } from 'react-router-dom'
import Badge from '../../components/common/Badge'
import Card from '../../components/common/Card'
import LoadingState from '../../components/common/LoadingState'
import SummaryStatCard from '../../components/trip/SummaryStatCard'
import { getRankings, ApiError } from '../../api/index'
import type { WorkspaceOutletContext } from '../../components/layout/TripWorkspaceLayout'
import type { RankingRow } from '../../types/vote'

const CATEGORY_LABEL: Record<string, string> = { attraction: '景點', restaurant: '餐廳' }

function calcDayCount(startDate: string, endDate: string): number {
  const start = new Date(startDate)
  const end = new Date(endDate)
  return Math.floor((end.getTime() - start.getTime()) / 86400000) + 1
}

export default function TripOverviewPage() {
  const { tripId } = useParams<{ tripId: string }>()
  const { trip } = useOutletContext<WorkspaceOutletContext>()

  const [rankings, setRankings] = useState<RankingRow[] | null>(null)
  const [rankingsLoading, setRankingsLoading] = useState(true)

  useEffect(() => {
    if (!tripId) return
    getRankings(tripId)
      .then(setRankings)
      .catch((err: unknown) => {
        if (err instanceof ApiError) {
          // non-critical: silently treat as empty
        }
        setRankings([])
      })
      .finally(() => setRankingsLoading(false))
  }, [tripId])

  // trip is guaranteed non-null here — layout handles tripLoading/tripError
  if (!trip) return null

  const metrics = [
    { label: '提案地點數', value: trip.summary.candidate_count },
    { label: '總投票數', value: trip.summary.vote_count },
    { label: '參與成員數', value: trip.summary.member_count },
    { label: '旅程天數', value: calcDayCount(trip.start_date, trip.end_date) },
  ]

  const topRankings = (rankings ?? []).slice(0, 4)

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
          <div className="p-5">
            {rankingsLoading ? (
              <LoadingState message="載入中…" className="py-6" />
            ) : topRankings.length === 0 ? (
              <p className="text-sm text-muted text-center py-6">尚無投票資料</p>
            ) : (
              <div className="flex flex-col gap-2.5">
                {topRankings.map((row) => (
                  <div
                    key={row.candidate_id}
                    className="flex items-center gap-3 px-4 py-3 bg-surface-soft rounded-xl"
                  >
                    <span className="text-sm font-bold text-muted w-5 text-center shrink-0">
                      {row.rank}
                    </span>
                    <span className="flex-1 text-sm font-medium text-ink min-w-0 truncate">
                      {row.name}
                    </span>
                    <Badge variant="neutral">
                      {CATEGORY_LABEL[row.category] ?? row.category}
                    </Badge>
                    <div className="flex items-center gap-1 shrink-0">
                      <span className="text-sm font-semibold text-ink">{row.vote_count}</span>
                      <span className="text-sm text-muted">票</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>

        {/* Quick actions */}
        <Card className="p-5 flex flex-col gap-2.5">
          <h3 className="text-base font-semibold text-ink mb-1">快速操作</h3>
          <Link
            to={`/trips/${tripId}/places`}
            className="flex items-center justify-between px-4 py-3 rounded-xl border border-line text-sm text-ink hover:bg-brand-soft transition-colors"
          >
            <span>前往地點</span>
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
            <span>查看行程表</span>
            <span className="text-brand-fg/70 text-sm">→</span>
          </Link>
        </Card>
      </div>
    </div>
  )
}
