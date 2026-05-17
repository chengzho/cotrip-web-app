import { Link } from 'react-router-dom'
import Card from '../common/Card'

export interface TripCardProps {
  trip_id: string;
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  role: 'owner' | 'member';
  member_count: number;
}

const roleLabel: Record<'owner' | 'member', string> = {
  owner: '擁有者',
  member: '成員',
}

function formatDateRange(start: string, end: string): string {
  const fmt = (d: string) => {
    const [y, m, day] = d.split('-');
    return `${y}/${parseInt(m)}/${parseInt(day)}`;
  };
  return `${fmt(start)} – ${fmt(end)}`;
}

export default function TripCard({
  trip_id,
  title,
  destination,
  start_date,
  end_date,
  role,
  member_count,
}: TripCardProps) {
  return (
    <Card shadow className="p-5 flex flex-col gap-4">
      <div>
        <h3 className="font-display text-base font-semibold text-ink leading-snug">
          {title}
        </h3>
      </div>

      <div className="flex flex-col gap-0.5">
        <p className="text-sm text-muted">{destination}</p>
        <p className="text-sm text-muted">{formatDateRange(start_date, end_date)}</p>
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-line">
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted">{member_count} 人 · {roleLabel[role]}</span>
        </div>
        <Link
          to={`/trips/${trip_id}`}
          className="inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium rounded-full border border-line text-ink hover:bg-brand-soft transition-colors"
        >
          開啟旅程
        </Link>
      </div>
    </Card>
  )
}
