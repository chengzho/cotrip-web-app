import { NavLink, useParams } from 'react-router-dom'

interface MobileBottomNavProps {
  onMoreClick: () => void
}

const navItems = [
  { label: '總覽', sub: '' },
  { label: '地點', sub: 'places' },
  { label: '投票', sub: 'voting' },
  { label: '行程', sub: 'itinerary' },
]

export default function MobileBottomNav({ onMoreClick }: MobileBottomNavProps) {
  const { tripId } = useParams<{ tripId: string }>()

  return (
    <nav
      className="flex items-stretch border-t border-line bg-surface shrink-0"
      style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
    >
      {navItems.map(({ label, sub }) => (
        <NavLink
          key={sub}
          to={sub ? `/trips/${tripId}/${sub}` : `/trips/${tripId}`}
          end={sub === ''}
          className={({ isActive }) =>
            [
              'flex-1 flex flex-col items-center justify-center py-2.5 text-xs transition-colors',
              isActive ? 'text-ink font-medium' : 'text-muted',
            ].join(' ')
          }
        >
          {label}
        </NavLink>
      ))}
      <button
        onClick={onMoreClick}
        className="flex-1 flex flex-col items-center justify-center py-2.5 text-xs text-muted hover:text-ink transition-colors"
      >
        更多
      </button>
    </nav>
  )
}
