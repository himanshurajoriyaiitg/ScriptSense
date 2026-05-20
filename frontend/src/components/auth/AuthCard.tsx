import type { ReactNode } from 'react'

type AuthCardProps = {
  title: string
  subtitle: string
  children: ReactNode
  footer: ReactNode
}

export function AuthCard({ title, subtitle, children, footer }: AuthCardProps) {
  return (
    <section className="glass-card relative overflow-hidden p-6 sm:p-8">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-200/80 to-transparent" />
      <header className="mb-7">
        <p className="text-sm font-semibold text-cyan-100">ScriptSense access</p>
        <h2 className="mt-3 text-3xl font-black leading-tight text-white">{title}</h2>
        <p className="mt-3 text-sm leading-6 text-slate-400">{subtitle}</p>
      </header>
      {children}
      <footer className="mt-6 border-t border-white/10 pt-5 text-center text-sm text-slate-400">{footer}</footer>
    </section>
  )
}
