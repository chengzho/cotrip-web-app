import { useEffect, useState } from 'react'
import { useOutletContext, useParams } from 'react-router-dom'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import RankingRow from '../../components/voting/RankingRow'
import { getRankings, voteCandidate, unvoteCandidate, ApiError } from '../../api/index'
import { CANDIDATE_CATEGORIES, CATEGORY_LABEL } from '../../constants/candidateCategories'
import type { CandidateCategory } from '../../constants/candidateCategories'
import type { WorkspaceOutletContext } from '../../components/layout/TripWorkspaceLayout'
import type { RankingRow as RankingRowType } from '../../types/vote'

type CategoryFilter = CandidateCategory | null

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

  const countByCategory = Object.fromEntries(
    CANDIDATE_CATEGORIES.map((cat) => [cat, rankings.filter((r) => r.category === cat).length])
  )

  const resolvedFilter: CategoryFilter =
    activeFilter && countByCategory[activeFilter] === 0 ? null : activeFilter

  // Category sections sorted by votes desc within each group (for all-categories grouped view)
  const grouped = CANDIDATE_CATEGORIES
    .map((cat) => ({
      category: cat,
      label: CATEGORY_LABEL[cat],
      items: rankings
        .filter((r) => r.category === cat)
        .sort((a, b) => b.vote_count - a.vote_count || a.candidate_id.localeCompare(b.candidate_id)),
    }))
    .filter((g) => g.items.length > 0)

  // Flat list for single-category filter view, sorted by votes desc
  const displayed = (resolvedFilter
    ? rankings.filter((r) => r.category === resolvedFilter)
    : rankings
  ).slice().sort((a, b) => b.vote_count - a.vote_count || a.candidate_id.localeCompare(b.candidate_id))

  const filterChips: { label: string; value: CategoryFilter; count: number }[] = [
    { label: '全部', value: null, count: rankings.length },
    ...CANDIDATE_CATEGORIES
      .filter((cat) => countByCategory[cat] > 0)
      .map((cat) => ({ label: CATEGORY_LABEL[cat], value: cat as CategoryFilter, count: countByCategory[cat] })),
  ]

  return (
    <div className="p-6 max-w-5xl">
      {/* Header */}
      <div className="mb-5">
        <h2 className="font-display text-xl font-semibold text-ink">群組投票</h2>
        {!loading && !error && (
          <p className="text-sm text-muted mt-1">
            {resolvedFilter
              ? `${displayed.length} 個地點 · ${CATEGORY_LABEL[resolvedFilter]}`
              : `${rankings.length} 個地點 · 依類型分組`}
          </p>
        )}
      </div>

      {voteError && (
        <p className="text-sm text-red-600 mb-4">{voteError}</p>
      )}

      {/* Tab-style category filter */}
      {!loading && !error && rankings.length > 0 && (
        <div className="flex items-center gap-0 border-b border-line mb-6 overflow-x-auto overflow-y-hidden">
          {filterChips.map(({ label, value, count }) => (
            <button
              key={label}
              type="button"
              onClick={() => setActiveFilter(value)}
              className={[
                'flex items-center gap-1.5 px-3 py-2.5 text-sm whitespace-nowrap transition-colors border-b-2 -mb-px focus:outline-none focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-ink',
                resolvedFilter === value
                  ? 'border-ink text-ink font-medium'
                  : 'border-transparent text-muted hover:text-ink',
              ].join(' ')}
            >
              {label}
              {value !== null && <span className="text-xs opacity-60">{count}</span>}
            </button>
          ))}
        </div>
      )}

      {/* Loading */}
      {loading && <LoadingState message="載入投票資料中…" />}

      {/* Error */}
      {!loading && error && (
        <ErrorState title="無法載入投票資料" message={error} />
      )}

      {/* No candidates at all */}
      {!loading && !error && rankings.length === 0 && (
        <EmptyState
          title="尚無投票資料"
          description="先新增候選地點，成員就可以開始投票了。"
        />
      )}

      {/* Filter active but category empty (safety net) */}
      {!loading && !error && resolvedFilter !== null && displayed.length === 0 && (
        <EmptyState title={`沒有${CATEGORY_LABEL[resolvedFilter]}地點`} />
      )}

      {/* Grouped all-categories view (default) */}
      {!loading && !error && resolvedFilter === null && grouped.length > 0 && (
        <div className="flex flex-col gap-3">
          {grouped.map(({ category, label, items }) => (
            <div key={category} className="rounded-xl border border-line bg-surface overflow-hidden">
              <div className="flex items-center gap-2 px-4 py-2.5 bg-background border-b border-line">
                <h3 className="text-sm font-semibold text-ink">{label}</h3>
                <span className="text-xs text-muted">{items.length}</span>
              </div>
              <div className="divide-y divide-line">
                {items.map((row, idx) => (
                  <RankingRow
                    key={row.candidate_id}
                    {...row}
                    rank={idx + 1}
                    showCategory={false}
                    variant="list"
                    onVote={() => handleVote(row.candidate_id, row.current_user_voted)}
                    voting={votingIds.has(row.candidate_id)}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Flat filtered view (single category selected) */}
      {!loading && !error && resolvedFilter !== null && displayed.length > 0 && (
        <div className="rounded-xl border border-line bg-surface overflow-hidden divide-y divide-line">
          {displayed.map((row, idx) => (
            <RankingRow
              key={row.candidate_id}
              {...row}
              rank={idx + 1}
              showCategory={false}
              variant="list"
              onVote={() => handleVote(row.candidate_id, row.current_user_voted)}
              voting={votingIds.has(row.candidate_id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
