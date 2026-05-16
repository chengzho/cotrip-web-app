import { Outlet } from 'react-router-dom'

export default function AppLayout() {
  return (
    <div className="min-h-svh">
      <Outlet />
    </div>
  )
}
