import Button from '../../components/common/Button'
import ItineraryDaySection from '../../components/itinerary/ItineraryDaySection'
import { type ItineraryItem } from '../../components/itinerary/ItineraryItemRow'

const day1: ItineraryItem[] = [
  {
    timeSlot: '上午',
    title: '伏見稻荷大社',
    note: '建議早晨 8 點前抵達，人潮較少。',
    category: '景點',
  },
  {
    timeSlot: '午餐',
    title: '錦市場',
    note: '逛市場小吃，品嚐京都傳統食材。',
    category: '餐廳',
  },
  {
    timeSlot: '下午',
    title: '金閣寺',
    note: '日式庭園與金箔建築，約需 1–2 小時。',
    category: '景點',
  },
]

const day2: ItineraryItem[] = [
  {
    timeSlot: '上午',
    title: '嵐山竹林小徑',
    note: '清晨竹林散步，附近有天龍寺。',
    category: '景點',
  },
  {
    timeSlot: '午餐',
    title: '湯豆腐餐廳',
    note: '嵐山傳統湯豆腐，清淡健康。',
    category: '餐廳',
  },
  {
    timeSlot: '晚餐',
    title: '一蘭拉麵 — 澀谷',
    note: '個人隔間豚骨拉麵，旅程最後一晚必去。',
    category: '餐廳',
  },
]

export default function TripItineraryPage() {
  return (
    <div className="p-6 max-w-5xl">
      {/* Header row */}
      <div className="flex items-start justify-between gap-4 mb-2">
        <h2 className="font-display text-xl font-semibold text-ink">行程表</h2>
        <div className="flex items-center gap-2 shrink-0">
          <Button variant="secondary" size="sm">重新產生</Button>
          <Button variant="secondary" size="sm">分享行程表</Button>
        </div>
      </div>

      {/* Summary */}
      <p className="text-sm text-muted mb-6">
        5 天 · 12 個地點 · 由群組投票結果產生
      </p>

      {/* Day sections */}
      <div className="flex flex-col gap-5">
        <ItineraryDaySection
          day={1}
          date="2024/3/25 (一)"
          city="京都"
          items={day1}
        />
        <ItineraryDaySection
          day={2}
          date="2024/3/26 (二)"
          city="京都 → 東京"
          items={day2}
        />
      </div>
    </div>
  )
}
