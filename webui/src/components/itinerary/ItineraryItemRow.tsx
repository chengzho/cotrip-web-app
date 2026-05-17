import Badge from '../common/Badge'

const CATEGORY_LABEL: Record<string, string> = { attraction: '景點', restaurant: '餐廳' }
const SLOT_LABEL: Record<string, string> = {
  morning: '上午',
  lunch: '午餐',
  afternoon: '下午',
  dinner: '晚餐',
  evening: '晚上',
}

export interface ItineraryItem {
  item_id: string;
  slot: string;
  title: string;
  category: string;
  note: string | null;
  sort_order: number;
}

type ItineraryItemRowProps = ItineraryItem & {
  onEdit?: () => void;
  onDelete?: () => void;
}

export default function ItineraryItemRow({
  slot,
  title,
  category,
  note,
  onEdit,
  onDelete,
}: ItineraryItemRowProps) {
  return (
    <div className="flex items-start gap-4 py-4 border-b border-line last:border-0">
      <span className="text-sm text-muted pt-0.5 w-12 shrink-0">
        {SLOT_LABEL[slot] ?? slot}
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-medium text-ink">{title}</span>
          <Badge variant="neutral">{CATEGORY_LABEL[category] ?? category}</Badge>
        </div>
        {note && <p className="text-sm text-muted mt-1">{note}</p>}
      </div>
      <div className="flex items-center gap-0.5 shrink-0">
        <button
          type="button"
          className="text-sm text-muted hover:text-ink px-2 py-1 rounded-lg hover:bg-brand-soft transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          onClick={onEdit}
          disabled={!onEdit}
        >
          編輯
        </button>
        <button
          type="button"
          className="text-sm text-muted hover:text-red-600 px-2 py-1 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          onClick={onDelete}
          disabled={!onDelete}
        >
          刪除
        </button>
      </div>
    </div>
  )
}
