import { useAuth } from '../../context/AuthContext'

interface AppHeaderProps {
  className?: string
}

export default function AppHeader({ className = '' }: AppHeaderProps) {
  const { user, signOut } = useAuth()

  return (
    <header
      className={[
        'sticky top-0 z-30 bg-surface border-b border-line',
        className,
      ].join(' ')}
    >
      <div className="max-w-5xl mx-auto px-5 h-14 flex items-center justify-between">
        <span className="font-display text-lg font-semibold tracking-tight text-ink">
          CoTrip
        </span>
        <div className="flex items-center gap-3">
          {user && (
            <span className="text-sm text-muted hidden sm:block">
              {user.displayName}
            </span>
          )}
          <div className="w-8 h-8 rounded-full bg-brand-soft border border-line flex items-center justify-center">
            <span className="text-sm font-medium text-ink select-none">
              {user ? user.initial : '旅'}
            </span>
          </div>
          <button
            type="button"
            onClick={signOut}
            className="text-sm text-muted hover:text-ink transition-colors hidden sm:block"
          >
            登出
          </button>
        </div>
      </div>
    </header>
  )
}
