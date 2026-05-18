import { Outlet } from 'react-router-dom'
import PublicHeader from './PublicHeader'
import { useAuth } from '../../context/AuthContext'

export default function PublicLayout() {
  const { authError } = useAuth()

  return (
    <div className="min-h-svh bg-background flex flex-col">
      <PublicHeader />
      {authError && (
        <div className="bg-red-50 border-b border-red-200 px-5 py-3 text-sm text-red-700 text-center">
          {authError}
        </div>
      )}
      <main className="flex-1 flex flex-col">
        <Outlet />
      </main>
    </div>
  )
}
