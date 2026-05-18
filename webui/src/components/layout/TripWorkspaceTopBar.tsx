import { useAuth } from '../../context/AuthContext'
import type { TripDetail } from '../../types/trip'

interface TripWorkspaceTopBarProps {
  trip: TripDetail | null;
}

function formatDate(d: string): string {
  const [y, m, day] = d.split('-')
  return `${y}/${parseInt(m)}/${parseInt(day)}`
}

export default function TripWorkspaceTopBar({ trip }: TripWorkspaceTopBarProps) {
  const { user, signOut } = useAuth()

  return (
    <div className="h-16 border-b border-line bg-surface px-6 flex items-center justify-between shrink-0">
      <div className="flex flex-col min-w-0">
        {trip ? (
          <>
            <span className="text-base font-semibold text-ink truncate">{trip.title}</span>
            <span className="text-sm text-muted truncate">
              {trip.destination} · {formatDate(trip.start_date)} – {formatDate(trip.end_date)}
            </span>
          </>
        ) : (
          <>
            <span className="text-base font-semibold text-muted truncate">載入中…</span>
            <span className="text-sm text-muted truncate">—</span>
          </>
        )}
      </div>
      <div className="flex items-center gap-4 ml-4 shrink-0">
        {trip && (
          <span className="text-sm text-muted">{trip.summary.member_count} 位成員</span>
        )}
        <button
          type="button"
          className="inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium rounded-full border border-line text-ink hover:bg-brand-soft transition-colors disabled:opacity-50"
          disabled
        >
          邀請朋友
        </button>
        {user && (
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-brand-soft border border-line flex items-center justify-center shrink-0">
              <span className="text-xs font-medium text-ink select-none">
                {user.initial}
              </span>
            </div>
            <button
              type="button"
              onClick={signOut}
              className="text-sm text-muted hover:text-ink transition-colors"
            >
              登出
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
