import { useState, type FormEvent } from 'react'
import Button from '../common/Button'
import Card from '../common/Card'
import FormError from '../common/FormError'
import {
  CANDIDATE_CATEGORIES,
  CATEGORY_LABEL,
  RESTAURANT_MEAL_TIMES,
  MEAL_TIME_LABEL,
} from '../../constants/candidateCategories'
import type { CandidateCategory, RestaurantMealTime } from '../../constants/candidateCategories'
import type { Candidate, CreateCandidateRequest } from '../../types/candidate'

interface CandidateFormPanelProps {
  initial?: Candidate;
  onSave: (data: CreateCandidateRequest) => Promise<void>;
  onCancel: () => void;
}

const inputClass = [
  'w-full border border-line rounded-xl px-4 py-3 text-sm text-ink bg-surface',
  'focus:outline-none focus:ring-1 focus:ring-ink/20',
  'transition-colors',
].join(' ')

const labelClass = 'block text-sm font-medium text-ink mb-1.5'

export default function CandidateFormPanel({ initial, onSave, onCancel }: CandidateFormPanelProps) {
  const [category, setCategory] = useState<CandidateCategory>(initial?.category ?? 'attraction')
  const [name, setName] = useState(initial?.name ?? '')
  const [address, setAddress] = useState(initial?.address ?? '')
  const [note, setNote] = useState(initial?.note ?? '')
  const [sourceUrl, setSourceUrl] = useState(initial?.source_url ?? '')
  const [mealTimes, setMealTimes] = useState<RestaurantMealTime[]>(
    initial?.restaurant_meal_times ?? []
  )
  const [areaLabel, setAreaLabel] = useState(initial?.area_label ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function handleCategoryChange(next: CandidateCategory) {
    setCategory(next)
    if (next !== 'restaurant') {
      setMealTimes([])
    }
  }

  function toggleMealTime(value: RestaurantMealTime) {
    setMealTimes((prev) => {
      if (value === 'any') {
        // selecting 'any' clears all others
        return prev.includes('any') ? [] : ['any']
      }
      // selecting a specific time clears 'any' if present
      const without = prev.filter((t) => t !== 'any' && t !== value)
      if (prev.includes(value)) {
        return without
      }
      return [...without, value]
    })
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!name.trim()) {
      setError('請輸入地點名稱。')
      return
    }
    setSaving(true)
    setError(null)
    try {
      await onSave({
        category,
        name: name.trim(),
        ...(address.trim() && { address: address.trim() }),
        ...(note.trim() && { note: note.trim() }),
        ...(sourceUrl.trim() && { source_url: sourceUrl.trim() }),
        ...(category === 'restaurant' && { restaurant_meal_times: mealTimes }),
        area_label: areaLabel.trim() || null,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : '儲存失敗，請稍後再試。')
      setSaving(false)
    }
  }

  return (
    <Card className="p-6 border-2 border-brand/40">
      <h3 className="text-base font-semibold text-ink mb-5">
        {initial ? '編輯地點' : '新增地點'}
      </h3>
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <div>
          <label className={labelClass}>類型</label>
          <select
            className={inputClass}
            value={category}
            onChange={(e) => handleCategoryChange(e.target.value as CandidateCategory)}
          >
            {CANDIDATE_CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>{CATEGORY_LABEL[cat]}</option>
            ))}
          </select>
        </div>

        {category === 'restaurant' && (
          <div>
            <label className={labelClass}>適合時段</label>
            <div className="flex flex-wrap gap-2">
              {RESTAURANT_MEAL_TIMES.map((mt) => {
                const selected = mealTimes.includes(mt)
                return (
                  <button
                    key={mt}
                    type="button"
                    onClick={() => toggleMealTime(mt)}
                    className={[
                      'px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors',
                      selected
                        ? 'bg-ink text-brand-fg border-ink'
                        : 'bg-surface text-muted border-line hover:border-ink/40 hover:text-ink',
                    ].join(' ')}
                  >
                    {MEAL_TIME_LABEL[mt]}
                  </button>
                )
              })}
            </div>
          </div>
        )}

        <div>
          <label className={labelClass}>地區</label>
          <input
            type="text"
            className={inputClass}
            value={areaLabel}
            onChange={(e) => setAreaLabel(e.target.value)}
            placeholder="選填，例：京都市區、大阪心齋橋"
          />
        </div>

        <div>
          <label className={labelClass}>名稱 <span className="text-red-500">*</span></label>
          <input
            type="text"
            className={inputClass}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="地點名稱"
          />
        </div>
        <div>
          <label className={labelClass}>地址</label>
          <input
            type="text"
            className={inputClass}
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="選填"
          />
        </div>
        <div>
          <label className={labelClass}>備註</label>
          <textarea
            rows={2}
            className={[inputClass, 'resize-none'].join(' ')}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="選填"
          />
        </div>
        <div>
          <label className={labelClass}>參考連結</label>
          <input
            type="url"
            className={inputClass}
            value={sourceUrl}
            onChange={(e) => setSourceUrl(e.target.value)}
            placeholder="選填"
          />
        </div>
        {error && <FormError message={error} />}
        <div className="flex gap-3 justify-end pt-2 border-t border-line">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={saving}>
            取消
          </Button>
          <Button type="submit" disabled={saving}>
            {saving ? '儲存中…' : initial ? '更新' : '新增'}
          </Button>
        </div>
      </form>
    </Card>
  )
}
