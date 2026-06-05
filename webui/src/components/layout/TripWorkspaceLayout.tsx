import { useCallback, useEffect, useState } from 'react'
import { Link, Outlet, useParams } from 'react-router-dom'
import WorkspaceSidebar from './WorkspaceSidebar'
import TripWorkspaceTopBar from './TripWorkspaceTopBar'
import MobileWorkspaceHeader from './MobileWorkspaceHeader'
import MobileBottomNav from './MobileBottomNav'
import MobileMoreSheet from './MobileMoreSheet'
import AppHeader from './AppHeader'
import LoadingState from '../common/LoadingState'
import { getTrip, ApiError } from '../../api/index'
import type { TripDetail } from '../../types/trip'

export interface WorkspaceOutletContext {
  trip: TripDetail | null;
  tripLoading: boolean;
  tripError: string | null;
  refreshTrip: () => Promise<void>;
}

export default function TripWorkspaceLayout() {
  const { tripId } = useParams<{ tripId: string }>()
  const [moreOpen, setMoreOpen] = useState(false)
  const [trip, setTrip] = useState<TripDetail | null>(null)
  const [tripLoading, setTripLoading] = useState(!!tripId)
  const [tripError, setTripError] = useState<string | null>(
    tripId ? null : '旅程 ID 無效。'
  )

  useEffect(() => {
    if (!tripId) return
    getTrip(tripId)
      .then(setTrip)
      .catch((err: unknown) => {
        if (err instanceof ApiError) {
          setTripError(err.isNotFound ? '找不到此旅程。' : err.isForbidden ? '你沒有權限查看此旅程。' : err.message)
        } else {
          setTripError('無法載入旅程，請稍後再試。')
        }
      })
      .finally(() => setTripLoading(false))
  }, [tripId])

  const refreshTrip = useCallback(async () => {
    if (!tripId) return
    try {
      const updated = await getTrip(tripId)
      setTrip(updated)
    } catch {
      // silent failure — page data remains current
    }
  }, [tripId])

  // Standalone fallback — no workspace chrome when the trip is inaccessible
  if (!tripLoading && tripError) {
    return (
      <div className="min-h-svh bg-background flex flex-col">
        <AppHeader />
        <main className="flex-1 flex items-center justify-center px-5 py-16">
          <div className="w-full max-w-sm text-center">
            <h1 className="font-display text-xl font-semibold text-ink mb-3">
              無法載入旅程
            </h1>
            <p className="text-sm text-muted mb-8 leading-relaxed">
              你沒有權限查看此旅程，或此旅程已不存在。<br />
              你可能已不在這趟旅程中。
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                to="/trips"
                className="inline-flex items-center justify-center px-5 py-2 text-sm font-medium rounded-full bg-brand text-brand-fg border border-transparent hover:opacity-90 transition-opacity"
              >
                回到我的旅程
              </Link>
              <Link
                to="/trips/new"
                className="inline-flex items-center justify-center px-5 py-2 text-sm font-medium rounded-full bg-transparent text-ink border border-line hover:bg-brand-soft transition-colors"
              >
                建立新旅程
              </Link>
            </div>
          </div>
        </main>
      </div>
    )
  }

  const outletContext: WorkspaceOutletContext = { trip, tripLoading, tripError, refreshTrip }

  return (
    <div className="flex min-h-svh bg-background">
      {/* Desktop sidebar — hidden on mobile */}
      <aside className="hidden md:flex">
        <WorkspaceSidebar />
      </aside>

      {/* Main column */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Desktop workspace top bar */}
        <div className="hidden md:block">
          <TripWorkspaceTopBar trip={trip} />
        </div>

        {/* Mobile compact header */}
        <div className="md:hidden">
          <MobileWorkspaceHeader trip={trip} />
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-surface-soft">
          {tripLoading ? (
            <LoadingState message="載入旅程中…" className="py-24" />
          ) : (
            <Outlet context={outletContext} />
          )}
        </main>

        {/* Mobile bottom nav */}
        <div className="md:hidden">
          <MobileBottomNav onMoreClick={() => setMoreOpen(true)} />
        </div>
      </div>

      {/* Mobile more sheet — rendered outside main column to avoid clipping */}
      <div className="md:hidden">
        <MobileMoreSheet open={moreOpen} onClose={() => setMoreOpen(false)} />
      </div>
    </div>
  )
}
