import type { ReactNode } from 'react'
import { BrainCircuit, ChartNoAxesCombined, FileScan, ScanSearch, ShieldCheck, Sparkles } from 'lucide-react'

type AuthLayoutProps = {
  eyebrow: string
  title: string
  subtitle: string
  children: ReactNode
}

const platformSignals = [
  { label: 'OCR confidence', value: '97.8%', icon: ScanSearch },
  { label: 'Rubric alignment', value: '94.2%', icon: BrainCircuit },
  { label: 'Review integrity', value: 'A+', icon: ShieldCheck },
]

export function AuthLayout({ eyebrow, title, subtitle, children }: AuthLayoutProps) {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#05060a] text-white">
      <div className="absolute inset-0 bg-[linear-gradient(135deg,#05060a_0%,#111827_42%,#0b231e_74%,#220f1f_100%)]" />
      <div className="absolute inset-0 animated-grid opacity-70" aria-hidden="true" />
      <div className="scan-band" aria-hidden="true" />

      <div className="relative z-10 mx-auto grid min-h-screen w-full max-w-7xl items-center gap-8 px-4 py-6 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8">
        <section className="hidden min-h-[42rem] flex-col justify-between lg:flex">
          <div>
            <div className="mb-8 inline-flex items-center gap-3 rounded-md border border-cyan-300/20 bg-cyan-300/10 px-4 py-2 text-sm font-semibold text-cyan-100 backdrop-blur">
              <Sparkles className="h-4 w-4" />
              {eyebrow}
            </div>

            <div className="max-w-2xl">
              <div className="mb-7 grid h-16 w-16 place-items-center rounded-lg border border-cyan-200/30 bg-white/10 shadow-[0_0_36px_rgba(34,211,238,0.24)] backdrop-blur">
                <FileScan className="h-8 w-8 text-cyan-100" />
              </div>
              <h1 className="max-w-3xl text-6xl font-black leading-[1.02] text-white">{title}</h1>
              <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">{subtitle}</p>
            </div>
          </div>

          <div className="grid gap-4">
            <div className="flex items-center gap-3 text-sm font-semibold text-emerald-100">
              <ChartNoAxesCombined className="h-5 w-5 text-emerald-200" />
              Live evaluation telemetry
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {platformSignals.map(({ icon: Icon, label, value }) => (
                <div className="glass-tile p-4" key={label}>
                  <Icon className="h-5 w-5 text-cyan-200" />
                  <p className="mt-5 text-2xl font-black text-white">{value}</p>
                  <p className="mt-1 text-sm text-slate-400">{label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto flex w-full max-w-lg flex-col gap-5">
          <div className="flex items-center gap-3 lg:hidden">
            <div className="grid h-11 w-11 place-items-center rounded-lg border border-cyan-200/25 bg-white/10">
              <FileScan className="h-5 w-5 text-cyan-100" />
            </div>
            <div>
              <p className="text-lg font-black text-white">ScriptSense</p>
              <p className="text-sm text-slate-400">AI exam evaluation</p>
            </div>
          </div>
          {children}
        </section>
      </div>
    </main>
  )
}
