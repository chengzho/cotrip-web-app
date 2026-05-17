import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import TripCard from '../components/trip/TripCard'
import LoadingState from '../components/common/LoadingState'
import ErrorState from '../components/common/ErrorState'
import EmptyState from '../components/common/EmptyState'
import { listTrips, ApiError } from '../api/index'
import type { TripSummary } from '../types/trip'

export default function TripsDashboardPage() {
  const [trips, setTrips] = useState<TripSummary[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    listTrips('upcoming')
      .then((data) => {
        setTrips(data)
      })
      .catch((err: unknown) => {
        if (err instanceof ApiError) {
          setErrorMessage(err.message)
        } else {
          setErrorMessage('無法載入旅程，請稍後再試。')
        }
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  return (
    <div className="max-w-5xl mx-auto px-5 py-10">
      {/* Greeting and primary CTA */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-5 mb-10">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">
            我的旅程
          </h1>
          {trips !== null && (
            <p className="text-sm text-muted mt-1.5">
              共 {trips.length} 趟即將到來的旅程
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

      {/* Trip cards area */}
      {loading && (
        <LoadingState message="載入旅程中…" />
      )}

      {!loading && errorMessage && (
        <ErrorState
          title="無法載入旅程"
          message={errorMessage}
          action={
            <button
              onClick={() => {
                setLoading(true)
                setErrorMessage(null)
                listTrips('upcoming')
                  .then(setTrips)
                  .catch((err: unknown) => {
                    setErrorMessage(
                      err instanceof ApiError ? err.message : '無法載入旅程，請稍後再試。'
                    )
                  })
                  .finally(() => setLoading(false))
              }}
              className="inline-flex items-center justify-center px-5 py-2 text-sm font-medium rounded-full border border-line text-ink hover:bg-brand-soft transition-colors"
            >
              重新整理
            </button>
          }
        />
      )}

      {!loading && !errorMessage && trips !== null && trips.length === 0 && (
        <EmptyState
          title="尚無旅程"
          description="建立第一趟旅程，邀請朋友一起規劃吧！"
          action={
            <Link
              to="/trips/new"
              className="inline-flex items-center justify-center px-5 py-2 text-sm font-medium rounded-full bg-brand text-brand-fg hover:opacity-90 transition-colors"
            >
              建立旅程
            </Link>
          }
        />
      )}

      {!loading && !errorMessage && trips !== null && trips.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {trips.map((trip) => (
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
