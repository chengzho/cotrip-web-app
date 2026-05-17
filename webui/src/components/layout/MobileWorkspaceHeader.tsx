import type { TripDetail } from '../../types/trip'

interface MobileWorkspaceHeaderProps {
  trip: TripDetail | null;
}

function formatDate(d: string): string {
  const [y, m, day] = d.split('-')
  return `${y}/${parseInt(m)}/${parseInt(day)}`
}

export default function MobileWorkspaceHeader({ trip }: MobileWorkspaceHeaderProps) {
  return (
    <header className="h-14 bg-surface border-b border-line px-4 flex items-center justify-between shrink-0">
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
      <button
        type="button"
        className="text-sm text-muted px-3 py-1.5 rounded-full border border-line hover:bg-brand-soft transition-colors disabled:opacity-50"
        disabled
      >
        邀請
      </button>
    </header>
  )
}
