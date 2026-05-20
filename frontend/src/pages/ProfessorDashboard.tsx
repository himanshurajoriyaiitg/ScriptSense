import { AlertTriangle, BookOpenCheck, CheckCircle2, FileStack, Gauge, UsersRound } from 'lucide-react'
import { DashboardLayout } from '../components/dashboard/DashboardLayout'
import { MetricCard } from '../components/dashboard/MetricCard'

const metrics = [
  {
    label: 'Scripts processed',
    value: '1,284',
    detail: 'Across five active courses',
    icon: FileStack,
    tone: 'cyan' as const,
  },
  {
    label: 'AI confidence',
    value: '96.4%',
    detail: 'Weighted by rubric variance',
    icon: Gauge,
    tone: 'emerald' as const,
  },
  {
    label: 'TA reviewers',
    value: '18',
    detail: 'Seven currently active',
    icon: UsersRound,
    tone: 'amber' as const,
  },
  {
    label: 'Escalations',
    value: '23',
    detail: 'Require professor validation',
    icon: AlertTriangle,
    tone: 'rose' as const,
  },
]

const reviewItems = ['Complex derivation responses', 'Low-confidence OCR segments', 'Rubric conflict flags']

export function ProfessorDashboard() {
  return (
    <DashboardLayout
      subtitle="Command center for grading quality, TA throughput, and audit-ready evaluation decisions."
      title="Professor dashboard"
    >
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => (
          <MetricCard key={metric.label} {...metric} />
        ))}
      </section>

      <section className="grid gap-4 py-6 lg:grid-cols-[1.05fr_0.95fr]">
        <article className="glass-card p-5">
          <div className="flex items-center gap-3">
            <BookOpenCheck className="h-5 w-5 text-cyan-100" />
            <h2 className="text-xl font-black text-white">Course evaluation stream</h2>
          </div>
          <div className="mt-6 grid gap-4">
            {['Data Structures midterm', 'AI foundations quiz', 'Compiler design finals'].map((course, index) => (
              <div className="border-b border-white/10 pb-4 last:border-0 last:pb-0" key={course}>
                <div className="flex items-center justify-between gap-4">
                  <p className="font-semibold text-slate-100">{course}</p>
                  <span className="rounded-md border border-emerald-300/20 bg-emerald-300/10 px-2 py-1 text-xs font-bold text-emerald-100">
                    {88 - index * 9}% complete
                  </span>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded-md bg-white/10">
                  <div
                    className="h-full rounded-md bg-gradient-to-r from-cyan-300 via-emerald-300 to-amber-200"
                    style={{ width: `${88 - index * 9}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="glass-card p-5">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="h-5 w-5 text-emerald-100" />
            <h2 className="text-xl font-black text-white">Attention queue</h2>
          </div>
          <div className="mt-6 grid gap-3">
            {reviewItems.map((item, index) => (
              <div className="flex items-center justify-between gap-4 border-b border-white/10 pb-3 last:border-0 last:pb-0" key={item}>
                <span className="text-sm font-semibold text-slate-200">{item}</span>
                <span className="text-sm font-black text-cyan-100">{index * 6 + 11}</span>
              </div>
            ))}
          </div>
        </article>
      </section>
    </DashboardLayout>
  )
}
