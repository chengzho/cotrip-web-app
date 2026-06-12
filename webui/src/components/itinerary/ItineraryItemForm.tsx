import { useState, useEffect, type FormEvent } from 'react'
import Button from '../common/Button'
import Card from '../common/Card'
import FormError from '../common/FormError'
import type { ItineraryItem } from './ItineraryItemRow'
import type { UpdateItineraryItemRequest, ItinerarySlot } from '../../types/itinerary'

interface ItineraryItemFormProps {
  item: ItineraryItem;
  dayNumber: number;
  onSave: (data: UpdateItineraryItemRequest) => Promise<void>;
  onCancel: () => void;
  onDirtyChange?: (dirty: boolean) => void;
}

const SLOT_OPTIONS: { value: ItinerarySlot; label: string }[] = [
  { value: 'morning', label: '上午' },
  { value: 'lunch', label: '午餐' },
  { value: 'afternoon', label: '下午' },
  { value: 'dinner', label: '晚餐' },
  { value: 'evening', label: '晚上' },
]

const inputClass = [
  'w-full border border-line rounded-xl px-4 py-3 text-sm text-ink bg-surface',
  'focus:outline-none focus:ring-1 focus:ring-ink/20',
  'transition-colors',
].join(' ')

const labelClass = 'block text-sm font-medium text-ink mb-1.5'

export default function ItineraryItemForm({ item, dayNumber, onSave, onCancel, onDirtyChange }: ItineraryItemFormProps) {
  // Captured once at mount; stable across re-renders because parent uses key={item_id}
  const [initial] = useState({
    slot: item.slot as ItinerarySlot,
    title: item.title,
    note: item.note ?? '',
    day: String(dayNumber),
    sortOrder: String(item.sort_order),
  })

  const [slot, setSlot] = useState<ItinerarySlot>(initial.slot)
  const [title, setTitle] = useState(initial.title)
  const [note, setNote] = useState(initial.note)
  const [day, setDay] = useState(initial.day)
  const [sortOrder, setSortOrder] = useState(initial.sortOrder)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const dirty =
      slot !== initial.slot ||
      title !== initial.title ||
      note !== initial.note ||
      day !== initial.day ||
      sortOrder !== initial.sortOrder
    onDirtyChange?.(dirty)
  }, [slot, title, note, day, sortOrder, initial, onDirtyChange])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!title.trim()) {
      setError('請輸入標題。')
      return
    }
    setSaving(true)
    setError(null)
    try {
      await onSave({
        slot,
        title: title.trim(),
        note: note.trim() || null,
        day_number: parseInt(day) || dayNumber,
        sort_order: parseInt(sortOrder) || item.sort_order,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : '儲存失敗，請稍後再試。')
      setSaving(false)
    }
  }

  return (
    <Card className="p-6 border-2 border-brand/40">
      <h3 className="text-base font-semibold text-ink mb-5">編輯行程項目</h3>
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <div>
          <label className={labelClass}>時段</label>
          <select
            className={inputClass}
            value={slot}
            onChange={(e) => setSlot(e.target.value as ItinerarySlot)}
          >
            {SLOT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>標題 <span className="text-red-500">*</span></label>
          <input
            type="text"
            className={inputClass}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
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
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>天數</label>
            <input
              type="number"
              min={1}
              className={inputClass}
              value={day}
              onChange={(e) => setDay(e.target.value)}
            />
          </div>
          <div>
            <label className={labelClass}>排序</label>
            <input
              type="number"
              min={1}
              className={inputClass}
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
            />
          </div>
        </div>
        {error && <FormError message={error} />}
        <div className="flex gap-3 justify-end pt-2 border-t border-line">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={saving}>
            取消
          </Button>
          <Button type="submit" disabled={saving}>
            {saving ? '儲存中…' : '更新'}
          </Button>
        </div>
      </form>
    </Card>
  )
}
