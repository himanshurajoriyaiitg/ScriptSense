import { AnimatedBackground } from "./AnimatedBackground";
import { BrandPanel } from "./BrandPanel";
import { LoginCard } from "./LoginCard";

export function ScriptSenseLogin() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.18),transparent_30%),linear-gradient(135deg,#020617_0%,#070b16_45%,#111827_100%)] px-4 py-6 text-white sm:px-6 lg:px-8">
      <AnimatedBackground />

      <div className="relative z-10 mx-auto grid min-h-[calc(100vh-3rem)] w-full max-w-7xl items-center gap-6 lg:grid-cols-[1.08fr_0.92fr]">
        <BrandPanel />

        <section className="mx-auto flex w-full max-w-md flex-col gap-6 lg:max-w-lg">
          <LoginCard />
          <p className="text-center text-sm leading-6 text-slate-500">
            Frontend-only prototype. Authentication is mocked locally for design validation.
          </p>
        </section>
      </div>
    </main>
  );
}
