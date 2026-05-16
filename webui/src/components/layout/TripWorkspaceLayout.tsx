import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import WorkspaceSidebar from './WorkspaceSidebar'
import TripWorkspaceTopBar from './TripWorkspaceTopBar'
import MobileWorkspaceHeader from './MobileWorkspaceHeader'
import MobileBottomNav from './MobileBottomNav'
import MobileMoreSheet from './MobileMoreSheet'

export default function TripWorkspaceLayout() {
  const [moreOpen, setMoreOpen] = useState(false)

  return (
    <div className="flex min-h-svh bg-background">
      {/* Desktop sidebar — hidden on mobile */}
      <aside className="hidden md:flex">
        <WorkspaceSidebar />
      </aside>

      {/* Main column */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Desktop workspace top bar */}
        <div className="hidden md:block">
          <TripWorkspaceTopBar />
        </div>

        {/* Mobile compact header */}
        <div className="md:hidden">
          <MobileWorkspaceHeader />
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>

        {/* Mobile bottom nav */}
        <div className="md:hidden">
          <MobileBottomNav onMoreClick={() => setMoreOpen(true)} />
        </div>
      </div>

      {/* Mobile more sheet — rendered outside main column to avoid clipping */}
      <div className="md:hidden">
        <MobileMoreSheet open={moreOpen} onClose={() => setMoreOpen(false)} />
      </div>
    </div>
  )
}
