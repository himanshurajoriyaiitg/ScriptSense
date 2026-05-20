import { ClipboardCheck, Clock3, FileQuestion, ListChecks, MessageSquareText, ScanLine } from 'lucide-react'
import { DashboardLayout } from '../components/dashboard/DashboardLayout'
import { MetricCard } from '../components/dashboard/MetricCard'

const metrics = [
  {
    label: 'Assigned scripts',
    value: '142',
    detail: 'Ready for assisted review',
    icon: ClipboardCheck,
    tone: 'cyan' as const,
  },
  {
    label: 'Pending checks',
    value: '37',
    detail: 'Flagged by rubric sensitivity',
    icon: ListChecks,
    tone: 'amber' as const,
  },
  {
    label: 'Avg. review time',
    value: '4.6m',
    detail: 'Per answer booklet',
    icon: Clock3,
    tone: 'emerald' as const,
  },
  {
    label: 'Clarifications',
    value: '8',
    detail: 'Awaiting professor response',
    icon: MessageSquareText,
    tone: 'rose' as const,
  },
]

const queue = [
  { title: 'Answer set A-214', signal: 'OCR mismatch', priority: 'High' },
  { title: 'Answer set C-091', signal: 'Rubric ambiguity', priority: 'Medium' },
  { title: 'Answer set F-338', signal: 'Diagram interpretation', priority: 'High' },
]

export function TaDashboard() {
  return (
    <DashboardLayout
      subtitle="Focused workspace for review queues, AI flags, and feedback handoff to professors."
      title="TA dashboard"
    >
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => (
          <MetricCard key={metric.label} {...metric} />
        ))}
      </section>

      <section className="grid gap-4 py-6 lg:grid-cols-[0.95fr_1.05fr]">
        <article className="glass-card p-5">
          <div className="flex items-center gap-3">
            <ScanLine className="h-5 w-5 text-cyan-100" />
            <h2 className="text-xl font-black text-white">Review rhythm</h2>
          </div>
          <div className="mt-6 grid gap-4">
            {['OCR verification', 'Rubric judgment', 'Feedback polish'].map((stage, index) => (
              <div className="grid gap-2" key={stage}>
                <div className="flex items-center justify-between gap-4">
                  <p className="text-sm font-semibold text-slate-200">{stage}</p>
                  <span className="text-sm font-black text-emerald-100">{76 + index * 7}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-md bg-white/10">
                  <div
                    className="h-full rounded-md bg-gradient-to-r from-cyan-300 via-emerald-300 to-amber-200"
                    style={{ width: `${76 + index * 7}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="glass-card p-5">
          <div className="flex items-center gap-3">
            <FileQuestion className="h-5 w-5 text-amber-100" />
            <h2 className="text-xl font-black text-white">Flagged scripts</h2>
          </div>
          <div className="mt-6 grid gap-3">
            {queue.map((item) => (
              <div className="grid gap-2 border-b border-white/10 pb-4 last:border-0 last:pb-0 sm:grid-cols-[1fr_auto] sm:items-center" key={item.title}>
                <div>
                  <p className="font-semibold text-slate-100">{item.title}</p>
                  <p className="mt-1 text-sm text-slate-500">{item.signal}</p>
                </div>
                <span className="w-fit rounded-md border border-cyan-300/20 bg-cyan-300/10 px-2 py-1 text-xs font-bold text-cyan-100">
                  {item.priority}
                </span>
              </div>
            ))}
          </div>
        </article>
      </section>
    </DashboardLayout>
  )
}
