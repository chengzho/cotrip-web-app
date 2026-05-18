import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Button from '../common/Button'

export default function PublicHeader() {
  const { isAuthenticated, signIn } = useAuth()

  return (
    <header className="sticky top-0 z-30 bg-surface/90 backdrop-blur-sm border-b border-line">
      <div className="max-w-5xl mx-auto px-5 h-14 flex items-center justify-between">
        <span className="font-display text-lg font-semibold tracking-tight text-ink">
          CoTrip
        </span>
        {isAuthenticated ? (
          <Link
            to="/trips"
            className="inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium rounded-full border border-line text-ink hover:bg-brand-soft transition-colors"
          >
            我的旅程
          </Link>
        ) : (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => { void signIn('/trips') }}
          >
            登入
          </Button>
        )}
      </div>
    </header>
  )
}
