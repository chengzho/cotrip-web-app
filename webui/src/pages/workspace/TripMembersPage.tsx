import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import Badge from '../../components/common/Badge'
import Card from '../../components/common/Card'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import InvitePanel from '../../components/members/InvitePanel'
import { listTripMembers, ApiError } from '../../api/index'
import type { TripMember } from '../../types/trip'

const ROLE_LABEL: Record<string, string> = { owner: '擁有者', member: '成員' }
type BadgeVariant = 'warm' | 'neutral'
const ROLE_BADGE: Record<string, BadgeVariant> = { owner: 'warm', member: 'neutral' }

export default function TripMembersPage() {
  const { tripId } = useParams<{ tripId: string }>()

  const [members, setMembers] = useState<TripMember[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!tripId) return
    listTripMembers(tripId)
      .then(setMembers)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : '無法載入成員資料，請稍後再試。')
      })
      .finally(() => setLoading(false))
  }, [tripId])

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
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Invite panel */}
        <InvitePanel tripId={tripId!} />
      </div>
    </div>
  )
}
