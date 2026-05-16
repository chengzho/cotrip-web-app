import { Link } from 'react-router-dom'
import AvatarGroup from '../common/AvatarGroup'
import Badge from '../common/Badge'
import Card from '../common/Card'

export type TripStatus = '規劃中' | '投票中' | '行程已完成'
export type TripRole = '擁有者' | '成員'

export interface TripCardProps {
  id: string
  title: string
  destination: string
  dateRange: string
  status: TripStatus
  members: { name: string }[]
  role: TripRole
}

const statusVariant: Record<TripStatus, 'neutral' | 'warm' | 'active'> = {
  規劃中: 'warm',
  投票中: 'active',
  行程已完成: 'neutral',
}

export default function TripCard({
  id,
  title,
  destination,
  dateRange,
  status,
  members,
  role,
}: TripCardProps) {
  return (
    <Card shadow className="p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-display text-base font-semibold text-ink leading-snug">
          {title}
        </h3>
        <Badge variant={statusVariant[status]} className="shrink-0">
          {status}
        </Badge>
      </div>

      <div className="flex flex-col gap-0.5">
        <p className="text-sm text-muted">{destination}</p>
        <p className="text-sm text-muted">{dateRange}</p>
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-line">
        <div className="flex items-center gap-2">
          <AvatarGroup avatars={members} size="sm" max={3} />
          <span className="text-xs text-muted">{role}</span>
        </div>
        <Link
          to={`/trips/${id}`}
          className="inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium rounded-full border border-line text-ink hover:bg-brand-soft transition-colors"
        >
          開啟旅程
        </Link>
      </div>
    </Card>
  )
}
