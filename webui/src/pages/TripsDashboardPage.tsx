import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import TripCard from '../components/trip/TripCard'
import LoadingState from '../components/common/LoadingState'
import DashboardStatePanel from '../components/trip/DashboardStatePanel'
import { listTrips, ApiError } from '../api/index'
import type { TripSummary } from '../types/trip'

type DashboardState =
  | { kind: 'loading' }
  | { kind: 'service-not-configured' }
  | { kind: 'empty' }
  | { kind: 'error'; message: string }
  | { kind: 'success'; trips: TripSummary[] }

// Evaluated once at module init — import.meta.env is a Vite compile-time constant.
const API_CONFIGURED = !!(
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? ''
).trim()

export default function TripsDashboardPage() {
  const [state, setState] = useState<DashboardState>(() =>
    API_CONFIGURED ? { kind: 'loading' } : { kind: 'service-not-configured' },
  )

  const fetchTrips = useCallback(() => {
    listTrips('upcoming')
      .then((data) => {
        setState(data.length === 0 ? { kind: 'empty' } : { kind: 'success', trips: data })
      })
      .catch((err: unknown) => {
        setState({
          kind: 'error',
          message: err instanceof ApiError ? err.message : '無法載入旅程，請稍後再試。',
        })
      })
  }, [])

  const retry = useCallback(() => {
    setState({ kind: 'loading' })
    fetchTrips()
  }, [fetchTrips])

  useEffect(() => {
    if (!API_CONFIGURED) return
    fetchTrips()
  }, [fetchTrips])

  return (
    <div className="max-w-5xl mx-auto px-5 py-10">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-5 mb-10">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">我的旅程</h1>
          {state.kind === 'success' && (
            <p className="text-sm text-muted mt-1.5">
              共 {state.trips.length} 趟即將到來的旅程
            </p>
          )}
        </div>
        <Link
          to="/trips/new"
          className="self-start inline-flex items-center justify-center px-5 py-2 text-sm font-medium rounded-full bg-brand text-brand-fg hover:opacity-90 transition-colors shrink-0"
        >
          建立旅程
        </Link>
      </div>

      {state.kind === 'loading' && <LoadingState message="載入旅程中…" />}

      {state.kind === 'service-not-configured' && (
        <DashboardStatePanel variant="service-not-configured" />
      )}

      {state.kind === 'empty' && <DashboardStatePanel variant="empty" />}

      {state.kind === 'error' && (
        <DashboardStatePanel variant="error" onRetry={retry} />
      )}

      {state.kind === 'success' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {state.trips.map((trip) => (
            <TripCard
              key={trip.trip_id}
              trip_id={trip.trip_id}
              title={trip.title}
              destination={trip.destination}
              start_date={trip.start_date}
              end_date={trip.end_date}
              role={trip.role}
              member_count={trip.member_count}
            />
          ))}
        </div>
      )}
    </div>
  )
}
