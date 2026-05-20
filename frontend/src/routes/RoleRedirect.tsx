import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { getDashboardPath } from '../lib/authStorage'

export function RoleRedirect() {
  const { user } = useAuth()

  return <Navigate to={user ? getDashboardPath(user.role) : '/login'} replace />
}
