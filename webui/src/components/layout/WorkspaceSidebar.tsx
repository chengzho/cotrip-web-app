import { Link, NavLink, useParams } from 'react-router-dom'

const navItems = [
  { label: '總覽', sub: '' },
  { label: '想去的地點', sub: 'places' },
  { label: '群組投票', sub: 'voting' },
  { label: '行程表', sub: 'itinerary' },
  { label: '成員', sub: 'members' },
  { label: '設定', sub: 'settings' },
]

export default function WorkspaceSidebar() {
  const { tripId } = useParams<{ tripId: string }>()

  return (
    <nav className="w-52 shrink-0 flex flex-col bg-surface border-r border-line">
      <div className="px-5 py-4 border-b border-line">
        <Link
          to="/trips"
          className="font-display text-base font-semibold tracking-tight text-ink hover:opacity-70 transition-opacity"
        >
          CoTrip
        </Link>
      </div>
      <ul className="px-3 py-3 flex flex-col gap-1">
        <li>
          <Link
            to="/trips"
            className="block px-3 py-2.5 rounded-lg text-base text-muted hover:bg-brand-soft hover:text-ink transition-colors"
          >
            我的旅程
          </Link>
        </li>
        <li className="my-1 border-t border-line" aria-hidden="true" />
        {navItems.map(({ label, sub }) => (
          <li key={sub}>
            <NavLink
              to={sub ? `/trips/${tripId}/${sub}` : `/trips/${tripId}`}
              end={sub === ''}
              className={({ isActive }) =>
                [
                  'block px-3 py-2.5 rounded-lg text-base transition-colors',
                  isActive
                    ? 'bg-brand-soft text-ink font-medium'
                    : 'text-muted hover:bg-brand-soft hover:text-ink',
                ].join(' ')
              }
            >
              {label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
