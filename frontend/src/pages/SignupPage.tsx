import type { FormEvent } from 'react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Loader2, Mail, UserRound } from 'lucide-react'
import { AuthCard } from '../components/auth/AuthCard'
import { AuthLayout } from '../components/auth/AuthLayout'
import { PasswordField } from '../components/auth/PasswordField'
import { RoleSelector } from '../components/auth/RoleSelector'
import { TextField } from '../components/auth/TextField'
import { useAuth } from '../context/useAuth'
import { getDashboardPath } from '../lib/authStorage'
import type { UserRole } from '../types/auth'

export function SignupPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<UserRole>('PROFESSOR')
  const [error, setError] = useState('')
  const [isPending, setIsPending] = useState(false)
  const { signup } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsPending(true)

    const result = await signup({ name, email, password, role })
    setIsPending(false)

    if (!result.ok || !result.user) {
      setError(result.message ?? 'Unable to create the account.')
      return
    }

    navigate(getDashboardPath(result.user.role), { replace: true })
  }

  return (
    <AuthLayout
      eyebrow="Local prototype access"
      subtitle="Create a local ScriptSense identity for professors or teaching assistants without any backend services."
      title="ScriptSense"
    >
      <AuthCard
        footer={
          <>
            Already have access?{' '}
            <Link className="font-semibold text-cyan-100 transition hover:text-white" to="/login">
              Sign in
            </Link>
          </>
        }
        subtitle="Your profile is stored locally in this browser and routed by role after signup."
        title="Create account"
      >
        <form className="grid gap-5" onSubmit={handleSubmit}>
          <TextField
            autoComplete="name"
            icon={UserRound}
            id="name"
            label="Full name"
            onChange={(event) => setName(event.target.value)}
            placeholder="Dr. Maya Kapoor"
            required
            type="text"
            value={name}
          />

          <TextField
            autoComplete="email"
            icon={Mail}
            id="email"
            inputMode="email"
            label="Email"
            onChange={(event) => setEmail(event.target.value)}
            placeholder="name@scriptsense.ai"
            required
            type="text"
            value={email}
          />

          <PasswordField autoComplete="new-password" onChange={setPassword} value={password} />
          <RoleSelector onChange={setRole} value={role} />

          {error && (
            <p className="rounded-md border border-rose-300/20 bg-rose-300/10 px-3 py-2 text-sm text-rose-100">
              {error}
            </p>
          )}

          <button
            className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-cyan-300 px-5 text-sm font-black text-slate-950 shadow-[0_0_30px_rgba(34,211,238,0.24)] transition duration-300 hover:-translate-y-0.5 hover:bg-cyan-200 focus:outline-none focus:ring-2 focus:ring-cyan-300/70 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:pointer-events-none disabled:opacity-70"
            disabled={isPending}
            type="submit"
          >
            {isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Sign up
          </button>
        </form>
      </AuthCard>
    </AuthLayout>
  )
}
