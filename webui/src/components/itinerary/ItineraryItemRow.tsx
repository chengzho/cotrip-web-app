import Badge from '../common/Badge'

export type TimeSlot = '上午' | '午餐' | '下午' | '晚餐'

export interface ItineraryItem {
  timeSlot: TimeSlot
  title: string
  note?: string
  category: '景點' | '餐廳'
}

export default function ItineraryItemRow({
  timeSlot,
  title,
  note,
  category,
}: ItineraryItem) {
  return (
    <div className="flex items-start gap-4 py-4 border-b border-line last:border-0">
      <span className="text-sm text-muted pt-0.5 w-12 shrink-0">{timeSlot}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-medium text-ink">{title}</span>
          <Badge variant="neutral">{category}</Badge>
        </div>
        {note && <p className="text-sm text-muted mt-1">{note}</p>}
      </div>
      <div className="flex items-center gap-0.5 shrink-0">
        <button
          type="button"
          className="text-sm text-muted hover:text-ink px-2 py-1 rounded-lg hover:bg-brand-soft transition-colors"
        >
          編輯
        </button>
        <button
          type="button"
          className="text-sm text-muted hover:text-ink px-2 py-1 rounded-lg hover:bg-brand-soft transition-colors"
        >
          刪除
        </button>
      </div>
    </div>
  )
}
