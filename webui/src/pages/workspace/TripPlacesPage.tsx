import { useEffect, useState } from 'react'
import { useOutletContext, useParams } from 'react-router-dom'
import Button from '../../components/common/Button'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import CandidatePlaceCard from '../../components/places/CandidatePlaceCard'
import CandidateFormPanel from '../../components/places/CandidateFormPanel'
import {
  listCandidates,
  createCandidate,
  updateCandidate,
  deleteCandidate,
  voteCandidate,
  unvoteCandidate,
  ApiError,
} from '../../api/index'
import { CANDIDATE_CATEGORIES, CATEGORY_LABEL } from '../../constants/candidateCategories'
import type { CandidateCategory } from '../../constants/candidateCategories'
import type { WorkspaceOutletContext } from '../../components/layout/TripWorkspaceLayout'
import type { Candidate, CreateCandidateRequest } from '../../types/candidate'

type CategoryFilter = CandidateCategory | null
type FormTarget = 'create' | Candidate | null

export default function TripPlacesPage() {
  const { tripId } = useParams<{ tripId: string }>()
  const { refreshTrip } = useOutletContext<WorkspaceOutletContext>()

  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeFilter, setActiveFilter] = useState<CategoryFilter>(null)
  const [formTarget, setFormTarget] = useState<FormTarget>(null)
  const [votingIds, setVotingIds] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (!tripId) return
    listCandidates(tripId)
      .then(setCandidates)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : '無法載入地點，請稍後再試。')
      })
      .finally(() => setLoading(false))
  }, [tripId])

  async function handleCreate(data: CreateCandidateRequest) {
    const created = await createCandidate(tripId!, data)
    setCandidates((prev) => [created, ...prev])
    setFormTarget(null)
    void refreshTrip()
  }

  async function handleUpdate(data: CreateCandidateRequest) {
    const target = formTarget as Candidate
    const updated = await updateCandidate(tripId!, target.candidate_id, data)
    setCandidates((prev) => prev.map((c) => c.candidate_id === updated.candidate_id ? updated : c))
    setFormTarget(null)
  }

  async function handleDelete(candidateId: string) {
    if (!window.confirm('確定要刪除此地點嗎？')) return
    try {
      await deleteCandidate(tripId!, candidateId)
      setCandidates((prev) => prev.filter((c) => c.candidate_id !== candidateId))
      void refreshTrip()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '刪除失敗，請稍後再試。')
    }
  }

  async function handleVote(candidateId: string, currentlyVoted: boolean) {
    setVotingIds((prev) => new Set([...prev, candidateId]))
    try {
      const result = await (currentlyVoted ? unvoteCandidate : voteCandidate)(candidateId)
      setCandidates((prev) => prev.map((c) =>
        c.candidate_id === result.candidate_id
          ? { ...c, vote_count: result.vote_count, current_user_voted: result.voted }
          : c
      ))
      void refreshTrip()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '投票操作失敗，請稍後再試。')
    } finally {
      setVotingIds((prev) => { const s = new Set(prev); s.delete(candidateId); return s })
    }
  }

  const countByCategory = Object.fromEntries(
    CANDIDATE_CATEGORIES.map((cat) => [cat, candidates.filter((c) => c.category === cat).length])
  )

  // Reset stale filter when selected category becomes empty (e.g. last candidate deleted)
  const resolvedFilter: CategoryFilter =
    activeFilter && countByCategory[activeFilter] === 0 ? null : activeFilter

  const displayed = resolvedFilter
    ? candidates.filter((c) => c.category === resolvedFilter)
    : candidates

  const filterChips: { label: string; value: CategoryFilter; count: number }[] = [
    { label: '全部', value: null, count: candidates.length },
    ...CANDIDATE_CATEGORIES
      .filter((cat) => countByCategory[cat] > 0)
      .map((cat) => ({ label: CATEGORY_LABEL[cat], value: cat as CategoryFilter, count: countByCategory[cat] })),
  ]

  return (
    <div className="p-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-5">
        <div>
          <h2 className="font-display text-xl font-semibold text-ink">想去的地點</h2>
          {!loading && !error && (
            <p className="text-sm text-muted mt-1">
              {candidates.length} 個提案
            </p>
          )}
        </div>
        {formTarget ? (
          <Button variant="secondary" className="shrink-0" onClick={() => setFormTarget(null)}>
            取消
          </Button>
        ) : (
          <Button className="shrink-0" onClick={() => setFormTarget('create')}>新增地點</Button>
        )}
      </div>

      {/* Create / Edit form */}
      {formTarget && (
        <div className="mb-6">
          <CandidateFormPanel
            initial={formTarget === 'create' ? undefined : formTarget}
            onSave={formTarget === 'create' ? handleCreate : handleUpdate}
            onCancel={() => setFormTarget(null)}
          />
        </div>
      )}

      {/* Tab-style category filter */}
      {!loading && !error && candidates.length > 0 && (
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
              <span className="text-xs opacity-60">{count}</span>
            </button>
          ))}
        </div>
      )}

      {/* States */}
      {loading && <LoadingState message="載入地點中…" />}

      {!loading && error && (
        <ErrorState title="無法載入地點" message={error} />
      )}

      {!loading && !error && candidates.length === 0 && (
        <EmptyState
          title="尚無提案地點"
          description="新增想去的景點或餐廳，一起和成員規劃吧！"
        />
      )}

      {!loading && !error && candidates.length > 0 && displayed.length === 0 && (
        <EmptyState title={`沒有${resolvedFilter ? CATEGORY_LABEL[resolvedFilter] : ''}地點`} />
      )}

      {!loading && !error && displayed.length > 0 && (
        <div className="flex flex-col gap-4">
          {displayed.map((c) => (
            <CandidatePlaceCard
              key={c.candidate_id}
              {...c}
              onEdit={() => setFormTarget(c)}
              onDelete={() => handleDelete(c.candidate_id)}
              onVote={() => handleVote(c.candidate_id, c.current_user_voted)}
              voting={votingIds.has(c.candidate_id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
