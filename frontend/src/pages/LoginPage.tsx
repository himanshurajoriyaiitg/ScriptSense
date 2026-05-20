import type { FormEvent } from 'react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Loader2, Mail } from 'lucide-react'
import { AuthCard } from '../components/auth/AuthCard'
import { AuthLayout } from '../components/auth/AuthLayout'
import { PasswordField } from '../components/auth/PasswordField'
import { RoleSelector } from '../components/auth/RoleSelector'
import { SocialLoginButton } from '../components/auth/SocialLoginButton'
import { TextField } from '../components/auth/TextField'
import { useAuth } from '../context/useAuth'
import { getDashboardPath } from '../lib/authStorage'
import type { AuthProvider, UserRole } from '../types/auth'

type SocialProvider = Exclude<AuthProvider, 'email'>
type PendingAction = 'email' | SocialProvider | null

const socialProviders: SocialProvider[] = ['Google', 'Facebook', 'Apple ID']

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<UserRole>('PROFESSOR')
  const [error, setError] = useState('')
  const [pendingAction, setPendingAction] = useState<PendingAction>(null)
  const { login, socialLogin } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setPendingAction('email')

    const result = await login({ email, password, role })
    setPendingAction(null)

    if (!result.ok || !result.user) {
      setError(result.message ?? 'Unable to sign in.')
      return
    }

    navigate(getDashboardPath(result.user.role), { replace: true })
  }

  const handleSocialLogin = async (provider: SocialProvider) => {
    setError('')
    setPendingAction(provider)
    const result = await socialLogin(provider, role)
    setPendingAction(null)

    if (result.user) {
      navigate(getDashboardPath(result.user.role), { replace: true })
    }
  }

  return (
    <AuthLayout
      eyebrow="Autonomous grading intelligence"
      subtitle="Sign in to monitor rubric scoring, review AI decisions, and keep evaluation workflows moving."
      title="ScriptSense"
    >
      <AuthCard
        footer={
          <>
            New to ScriptSense?{' '}
            <Link className="font-semibold text-cyan-100 transition hover:text-white" to="/signup">
              Create an account
            </Link>
          </>
        }
        subtitle="Use email credentials or a mocked identity provider to continue into the right workspace."
        title="Welcome back"
      >
        <form className="grid gap-5" onSubmit={handleSubmit}>
          <TextField
            autoComplete="email"
            icon={Mail}
            id="email"
            inputMode="email"
            label="Email"
            onChange={(event) => setEmail(event.target.value)}
            placeholder="professor@scriptsense.ai"
            required
            type="text"
            value={email}
          />

          <PasswordField autoComplete="current-password" onChange={setPassword} value={password} />
          <RoleSelector onChange={setRole} value={role} />

          {error && (
            <p className="rounded-md border border-rose-300/20 bg-rose-300/10 px-3 py-2 text-sm text-rose-100">
              {error}
            </p>
          )}

          <button
            className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-cyan-300 px-5 text-sm font-black text-slate-950 shadow-[0_0_30px_rgba(34,211,238,0.24)] transition duration-300 hover:-translate-y-0.5 hover:bg-cyan-200 focus:outline-none focus:ring-2 focus:ring-cyan-300/70 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:pointer-events-none disabled:opacity-70"
            disabled={Boolean(pendingAction)}
            type="submit"
          >
            {pendingAction === 'email' && <Loader2 className="h-4 w-4 animate-spin" />}
            Login
          </button>
        </form>

        <div className="my-5 flex items-center gap-4">
          <div className="h-px flex-1 bg-white/10" />
          <span className="text-xs font-bold text-slate-500">OR</span>
          <div className="h-px flex-1 bg-white/10" />
        </div>

        <div className="grid gap-2 sm:grid-cols-3">
          {socialProviders.map((provider) => (
            <SocialLoginButton
              isLoading={pendingAction === provider}
              key={provider}
              onClick={handleSocialLogin}
              provider={provider}
            />
          ))}
        </div>
      </AuthCard>
    </AuthLayout>
  )
}
