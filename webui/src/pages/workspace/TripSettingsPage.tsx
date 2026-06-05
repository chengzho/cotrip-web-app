import { useState, type FormEvent } from 'react'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import FormError from '../../components/common/FormError'
import SuccessMessage from '../../components/common/SuccessMessage'
import { updateTrip, deleteTrip, ApiError } from '../../api/index'
import type { WorkspaceOutletContext } from '../../components/layout/TripWorkspaceLayout'
import type { TripDetail } from '../../types/trip'

const inputClass = [
  'w-full border border-line rounded-xl px-4 py-3 text-sm text-ink bg-surface',
  'focus:outline-none focus:ring-1 focus:ring-ink/20',
  'transition-colors',
].join(' ')

const labelClass = 'block text-sm font-medium text-ink mb-1.5'

interface SettingsFormProps {
  trip: TripDetail;
  tripId: string;
  refreshTrip: () => Promise<void>;
}

function SettingsForm({ trip, tripId, refreshTrip }: SettingsFormProps) {
  const [baseline, setBaseline] = useState({
    title: trip.title,
    destination: trip.destination,
    startDate: trip.start_date,
    endDate: trip.end_date,
    description: trip.description ?? '',
  })
  const [title, setTitle] = useState(trip.title)
  const [destination, setDestination] = useState(trip.destination)
  const [startDate, setStartDate] = useState(trip.start_date)
  const [endDate, setEndDate] = useState(trip.end_date)
  const [description, setDescription] = useState(trip.description ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  function handleReset() {
    setTitle(baseline.title)
    setDestination(baseline.destination)
    setStartDate(baseline.startDate)
    setEndDate(baseline.endDate)
    setDescription(baseline.description)
    setError(null)
    setSuccess(false)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!title.trim() || !destination.trim() || !startDate || !endDate) {
      setError('請填寫所有必要欄位。')
      return
    }
    setSaving(true)
    setError(null)
    setSuccess(false)
    try {
      await updateTrip(tripId, {
        title: title.trim(),
        destination: destination.trim(),
        start_date: startDate,
        end_date: endDate,
        description: description.trim() || undefined,
      })
      const saved = {
        title: title.trim(),
        destination: destination.trim(),
        startDate,
        endDate,
        description: description.trim(),
      }
      setBaseline(saved)
      setSuccess(true)
      void refreshTrip()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '儲存失敗，請稍後再試。')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Card shadow className="p-6">
      <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
        {/* 旅程名稱 */}
        <div>
          <label className={labelClass}>旅程名稱</label>
          <input
            type="text"
            className={inputClass}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        {/* 目的地 */}
        <div>
          <label className={labelClass}>目的地</label>
          <input
            type="text"
            className={inputClass}
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
          />
        </div>

        {/* 日期 */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>開始日期</label>
            <input
              type="date"
              className={inputClass}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div>
            <label className={labelClass}>結束日期</label>
            <input
              type="date"
              className={inputClass}
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </div>

        {/* 描述 */}
        <div>
          <label className={labelClass}>描述</label>
          <textarea
            rows={4}
            className={[inputClass, 'resize-none'].join(' ')}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        {error && <FormError message={error} />}
        {success && <SuccessMessage message="設定已儲存。" />}

        {/* Actions */}
        <div className="flex gap-3 justify-end pt-2 border-t border-line mt-1">
          <Button type="button" variant="secondary" onClick={handleReset} disabled={saving}>
            放棄變更
          </Button>
          <Button type="submit" disabled={saving}>
            {saving ? '儲存中…' : '儲存變更'}
          </Button>
        </div>
      </form>
    </Card>
  )
}

interface DeleteTripSectionProps {
  tripId: string;
  tripTitle: string;
}

function DeleteTripSection({ tripId, tripTitle }: DeleteTripSectionProps) {
  const navigate = useNavigate()
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  async function handleDelete() {
    setDeleting(true)
    setDeleteError(null)
    try {
      await deleteTrip(tripId)
      navigate('/trips', { replace: true })
    } catch (err) {
      setDeleteError(err instanceof ApiError ? err.message : '刪除旅程失敗，請稍後再試。')
      setDeleting(false)
    }
  }

  return (
    <>
      <div className="rounded-xl border border-red-300 bg-red-50 p-6">
        <h3 className="text-base font-semibold text-red-700 mb-2">危險操作</h3>
        <p className="text-sm text-muted mb-5 leading-relaxed">
          刪除此旅程後，所有成員、邀請連結、提案地點、投票與行程表都會被永久移除。此操作無法復原。
        </p>
        <button
          type="button"
          onClick={() => { setConfirmOpen(true); setDeleteError(null) }}
          className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-full bg-red-600 text-white border border-transparent hover:bg-red-700 transition-colors"
        >
          刪除旅程
        </button>
      </div>

      {confirmOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onMouseDown={() => { if (!deleting) setConfirmOpen(false) }}
        >
          <div
            className="bg-surface rounded-xl border border-line shadow-lg w-full max-w-sm mx-4 p-6"
            onMouseDown={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-ink">刪除旅程？</h2>
              <button
                type="button"
                onClick={() => setConfirmOpen(false)}
                disabled={deleting}
                className="text-lg leading-none text-muted hover:text-ink transition-colors disabled:opacity-50"
                aria-label="關閉"
              >
                ✕
              </button>
            </div>
            <p className="text-sm text-muted mb-1 leading-relaxed">
              你即將刪除「<span className="font-medium text-ink">{tripTitle}</span>」。
            </p>
            <p className="text-sm text-muted mb-5 leading-relaxed">
              刪除後，所有成員、邀請連結、提案地點、投票與行程表都會永久移除。此操作無法復原。
            </p>
            {deleteError && (
              <p className="text-sm text-red-600 rounded-lg bg-red-50 px-4 py-2.5 border border-red-200 mb-4">
                {deleteError}
              </p>
            )}
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setConfirmOpen(false)} disabled={deleting}>
                取消
              </Button>
              <Button
                onClick={handleDelete}
                disabled={deleting}
                className="!bg-red-600 !border-red-600 hover:!opacity-90"
              >
                {deleting ? '刪除中…' : '刪除旅程'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default function TripSettingsPage() {
  const { tripId } = useParams<{ tripId: string }>()
  const { trip, tripLoading, tripError, refreshTrip } = useOutletContext<WorkspaceOutletContext>()

  if (tripLoading) {
    return <LoadingState message="載入設定中…" className="py-24" />
  }

  if (tripError || !trip) {
    return <ErrorState title="無法載入設定" message={tripError ?? undefined} className="py-24" />
  }

  const isOwner = trip.current_user_role === 'owner'

  return (
    <div className="p-6 max-w-3xl">
      {/* Page title */}
      <div className="mb-8">
        <h2 className="font-display text-xl font-semibold text-ink">旅程設定</h2>
        <p className="text-sm text-muted mt-1">修改旅程的基本資訊。</p>
      </div>

      <div className="flex flex-col gap-8">
        <SettingsForm key={trip.trip_id} trip={trip} tripId={tripId!} refreshTrip={refreshTrip} />

        {isOwner && (
          <DeleteTripSection tripId={tripId!} tripTitle={trip.title} />
        )}
      </div>
    </div>
  )
}
