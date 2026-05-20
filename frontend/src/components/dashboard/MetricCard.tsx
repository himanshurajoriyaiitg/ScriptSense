import type { LucideIcon } from 'lucide-react'

type MetricCardProps = {
  label: string
  value: string
  detail: string
  icon: LucideIcon
  tone: 'cyan' | 'emerald' | 'amber' | 'rose'
}

const toneClasses: Record<MetricCardProps['tone'], string> = {
  cyan: 'border-cyan-200/20 bg-cyan-300/10 text-cyan-100',
  emerald: 'border-emerald-200/20 bg-emerald-300/10 text-emerald-100',
  amber: 'border-amber-200/20 bg-amber-300/10 text-amber-100',
  rose: 'border-rose-200/20 bg-rose-300/10 text-rose-100',
}

export function MetricCard({ label, value, detail, icon: Icon, tone }: MetricCardProps) {
  return (
    <article className="glass-card p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-slate-400">{label}</p>
          <p className="mt-3 text-3xl font-black text-white">{value}</p>
        </div>
        <div className={`grid h-10 w-10 place-items-center rounded-lg border ${toneClasses[tone]}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <p className="mt-4 text-sm leading-6 text-slate-500">{detail}</p>
    </article>
  )
}
