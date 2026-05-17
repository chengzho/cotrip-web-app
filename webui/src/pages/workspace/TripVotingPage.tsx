import { useEffect, useState } from 'react'
import { useOutletContext, useParams } from 'react-router-dom'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import RankingRow from '../../components/voting/RankingRow'
import { getRankings, voteCandidate, unvoteCandidate, ApiError } from '../../api/index'
import type { WorkspaceOutletContext } from '../../components/layout/TripWorkspaceLayout'
import type { RankingRow as RankingRowType } from '../../types/vote'

type CategoryFilter = 'attraction' | 'restaurant' | null

const CATEGORY_LABEL: Record<string, string> = { attraction: '景點', restaurant: '餐廳' }

export default function TripVotingPage() {
  const { tripId } = useParams<{ tripId: string }>()
  const { refreshTrip } = useOutletContext<WorkspaceOutletContext>()

  const [rankings, setRankings] = useState<RankingRowType[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeFilter, setActiveFilter] = useState<CategoryFilter>(null)
  const [votingIds, setVotingIds] = useState<Set<string>>(new Set())
  const [voteError, setVoteError] = useState<string | null>(null)

  useEffect(() => {
    if (!tripId) return
    getRankings(tripId)
      .then(setRankings)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : '無法載入投票排行，請稍後再試。')
      })
      .finally(() => setLoading(false))
  }, [tripId])

  async function handleVote(candidateId: string, currentlyVoted: boolean) {
    setVotingIds((prev) => new Set([...prev, candidateId]))
    setVoteError(null)
    try {
      await (currentlyVoted ? unvoteCandidate : voteCandidate)(candidateId)
      const updated = await getRankings(tripId!)
      setRankings(updated)
      void refreshTrip()
    } catch (err) {
      setVoteError(err instanceof ApiError ? err.message : '投票操作失敗，請稍後再試。')
    } finally {
      setVotingIds((prev) => { const s = new Set(prev); s.delete(candidateId); return s })
    }
  }

  const displayed = activeFilter
    ? rankings.filter((r) => r.category === activeFilter)
    : rankings

  const attractionCount = rankings.filter((r) => r.category === 'attraction').length
  const restaurantCount = rankings.filter((r) => r.category === 'restaurant').length

  const filterChips: { label: string; value: CategoryFilter; count: number }[] = [
    { label: '全部', value: null, count: rankings.length },
    { label: CATEGORY_LABEL['attraction'], value: 'attraction', count: attractionCount },
    { label: CATEGORY_LABEL['restaurant'], value: 'restaurant', count: restaurantCount },
  ]

  return (
    <div className="p-6 max-w-5xl">
      {/* Header */}
      <div className="mb-6">
        <h2 className="font-display text-xl font-semibold text-ink">群組投票</h2>
        {!loading && !error && (
          <p className="text-sm text-muted mt-1">{rankings.length} 個地點 · 依票數排序</p>
        )}
      </div>

      {voteError && (
        <p className="text-sm text-red-600 mb-4">{voteError}</p>
      )}

      {/* Filter chips */}
      {!loading && !error && rankings.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap mb-6">
          {filterChips.map(({ label, value, count }) => (
            <button
              key={label}
              type="button"
              onClick={() => setActiveFilter(value)}
              className={[
                'inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm transition-colors',
                activeFilter === value
                  ? 'bg-ink text-brand-fg font-medium'
                  : 'bg-surface border border-line text-muted hover:bg-brand-soft hover:text-ink',
              ].join(' ')}
            >
              {label}
              <span className="text-xs opacity-70">{count}</span>
            </button>
          ))}
        </div>
      )}

      {/* States */}
      {loading && <LoadingState message="載入投票資料中…" />}

      {!loading && error && (
        <ErrorState title="無法載入投票資料" message={error} />
      )}

      {!loading && !error && rankings.length === 0 && (
        <EmptyState
          title="尚無投票資料"
          description="先新增候選地點，成員就可以開始投票了。"
        />
      )}

      {!loading && !error && rankings.length > 0 && displayed.length === 0 && (
        <EmptyState title={`沒有${activeFilter ? CATEGORY_LABEL[activeFilter] : ''}地點`} />
      )}

      {!loading && !error && displayed.length > 0 && (
        <div className="flex flex-col gap-3">
          {displayed.map((row) => (
            <RankingRow
              key={row.candidate_id}
              {...row}
              onVote={() => handleVote(row.candidate_id, row.current_user_voted)}
              voting={votingIds.has(row.candidate_id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
