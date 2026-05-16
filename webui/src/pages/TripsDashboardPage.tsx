import { Link } from 'react-router-dom'
import TripCard, { type TripCardProps } from '../components/trip/TripCard'

const mockTrips: TripCardProps[] = [
  {
    id: '1',
    title: '京都與東京春季之旅',
    destination: '日本',
    dateRange: '2024/3/25 – 4/5',
    status: '規劃中',
    members: [
      { name: 'Sophie' },
      { name: 'Alex' },
      { name: 'Jordan' },
      { name: 'Riley' },
    ],
    role: '擁有者',
  },
  {
    id: '2',
    title: '阿瑪菲海岸',
    destination: '義大利',
    dateRange: '2024/7/10 – 7/17',
    status: '投票中',
    members: [{ name: 'Sophie' }, { name: 'Morgan' }, { name: 'Taylor' }],
    role: '成員',
  },
  {
    id: '3',
    title: '里斯本週末旅行',
    destination: '葡萄牙',
    dateRange: '2024/9/13 – 9/16',
    status: '規劃中',
    members: [{ name: 'Sophie' }, { name: 'Casey' }],
    role: '擁有者',
  },
]

export default function TripsDashboardPage() {
  return (
    <div className="max-w-5xl mx-auto px-5 py-10">
      {/* Greeting and primary CTA */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-5 mb-10">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">
            嗨，Sophie
          </h1>
          <p className="text-sm text-muted mt-1.5">
            2 趟旅程規劃中 · 1 份行程已完成 · 共 3 趟旅程
          </p>
        </div>
        <Link
          to="/trips/new"
          className="self-start inline-flex items-center justify-center px-5 py-2 text-sm font-medium rounded-full bg-brand text-brand-fg hover:opacity-90 transition-colors shrink-0"
        >
          建立旅程
        </Link>
      </div>

      {/* Trip cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {mockTrips.map((trip) => (
          <TripCard key={trip.id} {...trip} />
        ))}
      </div>
    </div>
  )
}
