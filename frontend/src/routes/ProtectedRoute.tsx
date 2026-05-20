import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { getDashboardPath } from '../lib/authStorage'
import { useAuth } from '../context/useAuth'
import type { UserRole } from '../types/auth'

export function ProtectedRoute({ allowedRole }: { allowedRole: UserRole }) {
  const { user } = useAuth()
  const location = useLocation()

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (user.role !== allowedRole) {
    return <Navigate to={getDashboardPath(user.role)} replace />
  }

  return <Outlet />
}
