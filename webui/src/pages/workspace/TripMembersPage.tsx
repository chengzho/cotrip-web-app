import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import Badge from '../../components/common/Badge'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import InvitePanel from '../../components/members/InvitePanel'
import { listTripMembers, removeTripMember, ApiError } from '../../api/index'
import { useAuth } from '../../context/AuthContext'
import type { TripMember } from '../../types/trip'

const ROLE_LABEL: Record<string, string> = { owner: '擁有者', member: '成員' }
type BadgeVariant = 'warm' | 'neutral'
const ROLE_BADGE: Record<string, BadgeVariant> = { owner: 'warm', member: 'neutral' }

export default function TripMembersPage() {
  const { tripId } = useParams<{ tripId: string }>()
  const { profile } = useAuth()

  const [members, setMembers] = useState<TripMember[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [confirmTarget, setConfirmTarget] = useState<TripMember | null>(null)
  const [removing, setRemoving] = useState(false)
  const [removeError, setRemoveError] = useState<string | null>(null)

  const currentUserId = profile?.user_id ?? null
  const isOwner = members.some(m => m.user_id === currentUserId && m.role === 'owner')

  useEffect(() => {
    if (!tripId) return
    listTripMembers(tripId)
      .then(setMembers)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : '無法載入成員資料，請稍後再試。')
      })
      .finally(() => setLoading(false))
  }, [tripId])

  async function handleRemoveConfirm() {
    if (!tripId || !confirmTarget) return
    setRemoving(true)
    setRemoveError(null)
    try {
      await removeTripMember(tripId, confirmTarget.user_id)
      setMembers(prev => prev.filter(m => m.user_id !== confirmTarget.user_id))
      setConfirmTarget(null)
    } catch (err: unknown) {
      setRemoveError(err instanceof ApiError ? err.message : '移除成員失敗，請稍後再試。')
    } finally {
      setRemoving(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl">
      {/* Page title */}
      <div className="mb-6">
        <h2 className="font-display text-xl font-semibold text-ink">成員管理</h2>
        {!loading && !error && (
          <p className="text-sm text-muted mt-1">{members.length} 位成員參與此旅程</p>
        )}
      </div>

      {/* Two-column on lg: member list (wider) + invite panel (narrower) */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-5">
        {/* Member list */}
        <Card className="overflow-hidden">
          <div className="px-5 py-4 border-b border-line">
            <h3 className="text-base font-semibold text-ink">旅程成員</h3>
          </div>

          {loading && <LoadingState message="載入成員中…" className="py-10" />}

          {!loading && error && (
            <ErrorState title="無法載入成員" message={error} className="py-10" />
          )}

          {!loading && !error && members.length === 0 && (
            <EmptyState title="尚無成員資料" className="py-10" />
          )}

          {!loading && !error && members.length > 0 && (
            <div className="px-5">
              {members.map((member) => (
                <div
                  key={member.user_id}
                  className="flex items-center gap-4 py-5 border-b border-line last:border-0"
                >
                  <div className="w-10 h-10 rounded-full bg-brand-soft border border-line flex items-center justify-center shrink-0">
                    <span className="text-sm font-semibold text-ink select-none">
                      {member.display_name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-base font-medium text-ink truncate">
                      {member.display_name}
                    </p>
                    <p className="text-sm text-muted mt-0.5 truncate">{member.email}</p>
                  </div>
                  <Badge
                    variant={ROLE_BADGE[member.role] ?? 'neutral'}
                    className="shrink-0"
                  >
                    {ROLE_LABEL[member.role] ?? member.role}
                  </Badge>
                  {isOwner && member.role !== 'owner' && member.user_id !== currentUserId && (
                    <button
                      type="button"
                      onClick={() => { setConfirmTarget(member); setRemoveError(null) }}
                      className="shrink-0 text-sm text-muted hover:text-red-600 transition-colors px-2 py-1 rounded-lg hover:bg-red-50"
                    >
                      移除
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Invite panel */}
        <InvitePanel tripId={tripId!} />
      </div>

      {/* Remove member confirmation modal */}
      {confirmTarget && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onMouseDown={() => { if (!removing) setConfirmTarget(null) }}
        >
          <div
            className="bg-surface rounded-xl border border-line shadow-lg w-full max-w-sm mx-4 p-6"
            onMouseDown={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-ink">移除成員？</h2>
              <button
                type="button"
                onClick={() => setConfirmTarget(null)}
                disabled={removing}
                className="text-lg leading-none text-muted hover:text-ink transition-colors disabled:opacity-50"
                aria-label="關閉"
              >
                ✕
              </button>
            </div>
            <p className="text-sm text-muted mb-1 leading-relaxed">
              移除後，<span className="font-medium text-ink">{confirmTarget.display_name}</span> 將無法再進入這趟旅程。
            </p>
            <p className="text-sm text-muted mb-5 leading-relaxed">
              此成員在本旅程中的投票也會被移除，但已提案的地點會保留。
            </p>
            {removeError && (
              <p className="text-sm text-red-600 rounded-lg bg-red-50 px-4 py-2.5 border border-red-200 mb-4">
                {removeError}
              </p>
            )}
            <div className="flex justify-end gap-2">
              <Button
                variant="secondary"
                onClick={() => setConfirmTarget(null)}
                disabled={removing}
              >
                取消
              </Button>
              <Button
                onClick={handleRemoveConfirm}
                disabled={removing}
                className="!bg-red-600 !border-red-600 hover:!opacity-90"
              >
                {removing ? '移除中…' : '移除成員'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
