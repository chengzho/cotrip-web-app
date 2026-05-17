import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../components/common/Button'
import Card from '../components/common/Card'
import FormError from '../components/common/FormError'
import { createTrip, ApiError } from '../api/index'

const inputClass = [
  'w-full border border-line rounded-xl px-4 py-2.5 text-sm text-ink bg-surface',
  'placeholder:text-muted/60',
  'focus:outline-none focus:ring-1 focus:ring-ink/20',
  'transition-colors',
].join(' ')

const labelClass = 'block text-sm font-medium text-ink mb-1.5'

export default function CreateTripPage() {
  const navigate = useNavigate()

  const [title, setTitle] = useState('')
  const [destination, setDestination] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [description, setDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  function validate(): string | null {
    if (!title.trim()) return '請填寫旅程名稱。'
    if (!destination.trim()) return '請填寫目的地。'
    if (!startDate) return '請選擇開始日期。'
    if (!endDate) return '請選擇結束日期。'
    if (endDate < startDate) return '結束日期不可早於開始日期。'
    return null
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const validationError = validate()
    if (validationError) {
      setFormError(validationError)
      return
    }
    setFormError(null)
    setSubmitting(true)
    try {
      const trip = await createTrip({
        title: title.trim(),
        destination: destination.trim(),
        start_date: startDate,
        end_date: endDate,
        description: description.trim() || undefined,
      })
      navigate(`/trips/${trip.trip_id}`)
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setFormError(err.message)
      } else {
        setFormError('建立旅程失敗，請稍後再試。')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-5 py-10">
      <div className="max-w-lg mx-auto">
        {/* Page header */}
        <div className="mb-8">
          <h1 className="font-display text-2xl font-semibold text-ink">
            建立旅程
          </h1>
          <p className="text-sm text-muted mt-2">
            填寫基本資訊，開始邀請朋友協作規劃。
          </p>
        </div>

        {/* Form card */}
        <Card shadow className="p-6">
          <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
            {/* 旅程名稱 */}
            <div>
              <label className={labelClass}>旅程名稱</label>
              <input
                type="text"
                placeholder="例：京都與東京春季之旅"
                className={inputClass}
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={submitting}
              />
            </div>

            {/* 目的地 */}
            <div>
              <label className={labelClass}>目的地</label>
              <input
                type="text"
                placeholder="例：日本"
                className={inputClass}
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                disabled={submitting}
              />
            </div>

            {/* 日期 — side by side */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>開始日期</label>
                <input
                  type="date"
                  className={inputClass}
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  disabled={submitting}
                />
              </div>
              <div>
                <label className={labelClass}>結束日期</label>
                <input
                  type="date"
                  className={inputClass}
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  disabled={submitting}
                />
              </div>
            </div>

            {/* 描述 */}
            <div>
              <label className={labelClass}>描述</label>
              <textarea
                rows={4}
                placeholder="簡短說明這趟旅程的主題或目標（選填）"
                className={[inputClass, 'resize-none'].join(' ')}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={submitting}
              />
            </div>

            {/* Form-level error */}
            {formError && <FormError message={formError} />}

            {/* Actions */}
            <div className="flex gap-3 justify-end pt-2 border-t border-line mt-1">
              <Button
                type="button"
                variant="secondary"
                disabled={submitting}
                onClick={() => navigate('/trips')}
              >
                取消
              </Button>
              <Button type="submit" disabled={submitting}>
                {submitting ? '建立中…' : '建立旅程'}
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  )
}
