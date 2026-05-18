import { Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Button from '../common/Button'
import LoadingState from '../common/LoadingState'

export default function RequireAuth() {
  const { isAuthenticated, isInitializing, signIn } = useAuth()
  const { pathname } = useLocation()

  if (isInitializing) {
    return (
      <div className="min-h-svh flex items-center justify-center">
        <LoadingState message="驗證身分中…" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-svh flex items-center justify-center px-5">
        <div className="text-center max-w-sm">
          <p className="font-display text-xl font-semibold text-ink mb-2">
            需要登入
          </p>
          <p className="text-sm text-muted mb-6">
            請先登入以繼續使用 CoTrip。
          </p>
          <Button onClick={() => { void signIn(pathname) }}>前往登入</Button>
        </div>
      </div>
    )
  }

  return <Outlet />
}
