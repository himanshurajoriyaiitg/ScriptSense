import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { LoginPage } from './pages/LoginPage'
import { ProfessorDashboard } from './pages/ProfessorDashboard'
import { SignupPage } from './pages/SignupPage'
import { TaDashboard } from './pages/TaDashboard'
import { ProtectedRoute } from './routes/ProtectedRoute'
import { PublicRoute } from './routes/PublicRoute'
import { RoleRedirect } from './routes/RoleRedirect'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
          </Route>

          <Route element={<ProtectedRoute allowedRole="PROFESSOR" />}>
            <Route path="/professor" element={<ProfessorDashboard />} />
          </Route>

          <Route element={<ProtectedRoute allowedRole="TA" />}>
            <Route path="/ta" element={<TaDashboard />} />
          </Route>

          <Route path="/" element={<RoleRedirect />} />
          <Route path="*" element={<RoleRedirect />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
