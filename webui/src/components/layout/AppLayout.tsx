import { Outlet } from 'react-router-dom'
import AppHeader from './AppHeader'

export default function AppLayout() {
  return (
    <div className="min-h-svh bg-background flex flex-col">
      <AppHeader />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}
