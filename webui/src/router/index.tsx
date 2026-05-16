import { createBrowserRouter } from 'react-router-dom'
import PublicLayout from '../components/layout/PublicLayout'
import AppLayout from '../components/layout/AppLayout'
import TripWorkspaceLayout from '../components/layout/TripWorkspaceLayout'
import LandingPage from '../pages/LandingPage'
import TripsDashboardPage from '../pages/TripsDashboardPage'
import CreateTripPage from '../pages/CreateTripPage'
import JoinInvitePage from '../pages/JoinInvitePage'
import TripOverviewPage from '../pages/workspace/TripOverviewPage'
import TripPlacesPage from '../pages/workspace/TripPlacesPage'
import TripVotingPage from '../pages/workspace/TripVotingPage'
import TripItineraryPage from '../pages/workspace/TripItineraryPage'
import TripMembersPage from '../pages/workspace/TripMembersPage'
import TripSettingsPage from '../pages/workspace/TripSettingsPage'
import NotFoundPage from '../pages/NotFoundPage'

const router = createBrowserRouter(
  [
    {
      element: <PublicLayout />,
      children: [
        { path: '/', element: <LandingPage /> },
        { path: '/join/:inviteToken', element: <JoinInvitePage /> },
      ],
    },
    {
      element: <AppLayout />,
      children: [
        { path: '/trips', element: <TripsDashboardPage /> },
        { path: '/trips/new', element: <CreateTripPage /> },
      ],
    },
    {
      path: '/trips/:tripId',
      element: <TripWorkspaceLayout />,
      children: [
        { index: true, element: <TripOverviewPage /> },
        { path: 'places', element: <TripPlacesPage /> },
        { path: 'voting', element: <TripVotingPage /> },
        { path: 'itinerary', element: <TripItineraryPage /> },
        { path: 'members', element: <TripMembersPage /> },
        { path: 'settings', element: <TripSettingsPage /> },
      ],
    },
    { path: '*', element: <NotFoundPage /> },
  ],
  { basename: import.meta.env.BASE_URL },
)

export default router
