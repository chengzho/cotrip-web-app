import Badge from '../common/Badge'
import Card from '../common/Card'
import ItineraryItemRow, { type ItineraryItem } from './ItineraryItemRow'

interface ItineraryDaySectionProps {
  day: number
  date: string
  city?: string
  items: ItineraryItem[]
}

export default function ItineraryDaySection({
  day,
  date,
  city,
  items,
}: ItineraryDaySectionProps) {
  return (
    <Card className="overflow-hidden">
      <div className="px-6 py-4 bg-surface-soft/60 border-b border-line flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Badge variant="warm">Day {day}</Badge>
          <div>
            <p className="text-sm font-semibold text-ink">{date}</p>
            {city && <p className="text-sm text-muted mt-0.5">{city}</p>}
          </div>
        </div>
        <span className="text-sm text-muted">{items.length} 個地點</span>
      </div>
      <div className="px-6">
        {items.map((item, i) => (
          <ItineraryItemRow key={i} {...item} />
        ))}
      </div>
    </Card>
  )
}
