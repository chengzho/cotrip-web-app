import { Outlet } from 'react-router-dom'
import PublicHeader from './PublicHeader'

export default function PublicLayout() {
  return (
    <div className="min-h-svh bg-background flex flex-col">
      <PublicHeader />
      <main className="flex-1 flex flex-col">
        <Outlet />
      </main>
    </div>
  )
}
