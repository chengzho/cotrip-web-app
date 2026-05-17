import { useState, type FormEvent } from 'react'
import { useOutletContext, useParams } from 'react-router-dom'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import FormError from '../../components/common/FormError'
import SuccessMessage from '../../components/common/SuccessMessage'
import { updateTrip, ApiError } from '../../api/index'
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

export default function TripSettingsPage() {
  const { tripId } = useParams<{ tripId: string }>()
  const { trip, tripLoading, tripError, refreshTrip } = useOutletContext<WorkspaceOutletContext>()

  if (tripLoading) {
    return <LoadingState message="載入設定中…" className="py-24" />
  }

  if (tripError || !trip) {
    return <ErrorState title="無法載入設定" message={tripError ?? undefined} className="py-24" />
  }

  return (
    <div className="p-6 max-w-3xl">
      {/* Page title */}
      <div className="mb-8">
        <h2 className="font-display text-xl font-semibold text-ink">旅程設定</h2>
        <p className="text-sm text-muted mt-1">修改旅程的基本資訊。</p>
      </div>

      <SettingsForm key={trip.trip_id} trip={trip} tripId={tripId!} refreshTrip={refreshTrip} />
    </div>
  )
}
