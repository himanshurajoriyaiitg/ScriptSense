import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { getDashboardPath } from '../lib/authStorage'

export function PublicRoute() {
  const { user } = useAuth()

  if (user) {
    return <Navigate to={getDashboardPath(user.role)} replace />
  }

  return <Outlet />
}
