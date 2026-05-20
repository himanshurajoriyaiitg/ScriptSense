import {
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  FileScan,
  ScanText,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

const features = [
  { icon: ScanText, text: "OCR-based answer extraction" },
  { icon: BrainCircuit, text: "AI rubric grading" },
  { icon: ShieldCheck, text: "Human-in-the-loop review" },
  { icon: BarChart3, text: "Analytics dashboard" },
];

export function BrandPanel() {
  return (
    <section className="relative flex min-h-[36rem] flex-col justify-between overflow-hidden rounded-lg border border-white/10 bg-white/[0.035] p-8 shadow-inner-glow backdrop-blur md:p-10 lg:min-h-[48rem] lg:p-12">
      <div className="absolute right-8 top-8 hidden h-40 w-40 rounded-full border border-cyan-300/20 lg:block" />
      <div className="absolute right-14 top-14 hidden h-28 w-28 rounded-full border border-violet-300/20 lg:block" />

      <div className="relative z-10">
        <div className="mb-10 inline-flex items-center gap-3 rounded-md border border-cyan-300/20 bg-cyan-300/10 px-4 py-2 text-sm font-medium text-cyan-100">
          <Sparkles className="h-4 w-4" />
          Autonomous exam intelligence
        </div>

        <div className="flex items-center gap-4">
          <div className="grid h-16 w-16 place-items-center rounded-lg border border-cyan-300/35 bg-cyan-300/15 shadow-glow">
            <FileScan className="h-8 w-8 text-cyan-200" />
          </div>
          <div>
            <h1 className="text-4xl font-black tracking-normal text-white sm:text-5xl lg:text-6xl">
              ScriptSense
            </h1>
            <p className="mt-3 max-w-2xl text-lg leading-8 text-slate-300 sm:text-xl">
              AI-Powered Handwritten Exam Evaluation Platform
            </p>
          </div>
        </div>

        <div className="mt-12 grid gap-4 sm:grid-cols-2">
          {features.map(({ icon: Icon, text }) => (
            <div className="feature-tile rounded-lg p-4" key={text}>
              <Icon className="mb-4 h-5 w-5 text-cyan-200" />
              <p className="text-sm font-medium leading-6 text-slate-200">{text}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="relative z-10 mt-12 grid gap-4 rounded-lg border border-white/10 bg-slate-950/45 p-5 backdrop-blur">
        <div className="flex items-center justify-between gap-6">
          <div>
            <p className="text-sm text-slate-400">Evaluation accuracy</p>
            <p className="mt-1 text-3xl font-black text-white">98.4%</p>
          </div>
          <CheckCircle2 className="h-10 w-10 text-cyan-200" />
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-white/10">
          <div className="h-full w-[82%] rounded-full bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400" />
        </div>
        <p className="text-sm leading-6 text-slate-400">
          Rubric-aware scoring, review queues, and audit-ready feedback in one secure workspace.
        </p>
      </div>
    </section>
  );
}
