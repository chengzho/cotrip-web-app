import Badge from '../common/Badge'
import Card from '../common/Card'
import ItineraryItemRow, { type ItineraryItem } from './ItineraryItemRow'

const SLOT_ORDER: Record<string, number> = {
  morning: 0,
  lunch: 1,
  afternoon: 2,
  dinner: 3,
  evening: 4,
}

function formatDate(d: string): string {
  const [y, m, day] = d.split('-')
  return `${y}/${parseInt(m)}/${parseInt(day)}`
}

interface ItineraryDaySectionProps {
  day_number: number;
  date: string;
  items: ItineraryItem[];
  onEditItem?: (item: ItineraryItem, dayNumber: number) => void;
  onDeleteItem?: (item: ItineraryItem) => void;
}

export default function ItineraryDaySection({
  day_number,
  date,
  items,
  onEditItem,
  onDeleteItem,
}: ItineraryDaySectionProps) {
  const sortedItems = [...items].sort((a, b) => {
    const slotDiff = (SLOT_ORDER[a.slot] ?? 99) - (SLOT_ORDER[b.slot] ?? 99)
    if (slotDiff !== 0) return slotDiff
    const orderDiff = a.sort_order - b.sort_order
    if (orderDiff !== 0) return orderDiff
    return a.item_id.localeCompare(b.item_id)
  })

  return (
    <Card className="overflow-hidden">
      <div className="px-6 py-4 bg-surface-soft/60 border-b border-line flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Badge variant="warm">Day {day_number}</Badge>
          <div>
            <p className="text-sm font-semibold text-ink">{formatDate(date)}</p>
          </div>
        </div>
        <span className="text-sm text-muted">{items.length} 個地點</span>
      </div>
      <div className="px-6">
        {sortedItems.map((item) => (
          <ItineraryItemRow
            key={item.item_id}
            {...item}
            onEdit={onEditItem ? () => onEditItem(item, day_number) : undefined}
            onDelete={onDeleteItem ? () => onDeleteItem(item) : undefined}
          />
        ))}
      </div>
    </Card>
  )
}
