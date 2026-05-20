import type { ReactNode } from 'react'
import { BrainCircuit, FileScan, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'

type DashboardLayoutProps = {
  title: string
  subtitle: string
  children: ReactNode
}

export function DashboardLayout({ title, subtitle, children }: DashboardLayoutProps) {
  const { logout, user } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#05060a] text-white">
      <div className="absolute inset-0 bg-[linear-gradient(135deg,#05060a_0%,#111827_46%,#10251f_78%,#26111c_100%)]" />
      <div className="absolute inset-0 animated-grid opacity-60" aria-hidden="true" />
      <div className="scan-band" aria-hidden="true" />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-5 sm:px-6 lg:px-8">
        <header className="glass-nav flex flex-wrap items-center justify-between gap-4 px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-lg border border-cyan-200/25 bg-cyan-200/10">
              <FileScan className="h-5 w-5 text-cyan-100" />
            </div>
            <div>
              <p className="text-lg font-black text-white">ScriptSense</p>
              <p className="text-sm text-slate-500">{user?.role === 'PROFESSOR' ? 'Professor' : 'TA'} workspace</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-md border border-emerald-300/20 bg-emerald-300/10 px-3 py-2 text-sm font-semibold text-emerald-100 sm:flex">
              <BrainCircuit className="h-4 w-4" />
              AI online
            </div>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-white/10 bg-white/[0.06] px-3 text-sm font-semibold text-slate-200 transition hover:border-rose-200/40 hover:bg-rose-400/10 hover:text-white focus:outline-none focus:ring-2 focus:ring-cyan-300/60"
              onClick={handleLogout}
              type="button"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </header>

        <section className="py-8 sm:py-10">
          <p className="text-sm font-semibold text-cyan-100">{user?.name}</p>
          <h1 className="mt-3 max-w-4xl text-4xl font-black leading-tight text-white sm:text-5xl">{title}</h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-slate-400">{subtitle}</p>
        </section>

        {children}
      </div>
    </main>
  )
}
