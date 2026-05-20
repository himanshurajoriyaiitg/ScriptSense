export function AnimatedBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div className="absolute -left-24 top-12 h-80 w-80 animate-float rounded-full bg-cyan-400/20 blur-3xl" />
      <div className="absolute bottom-0 right-[-7rem] h-96 w-96 animate-float rounded-full bg-violet-500/20 blur-3xl [animation-delay:1.2s]" />
      <div className="absolute left-[42%] top-[18%] h-56 w-56 animate-glow-pulse rounded-full bg-blue-500/10 blur-3xl" />
      <div className="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.045)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.045)_1px,transparent_1px)] bg-[size:72px_72px] [mask-image:radial-gradient(circle_at_center,black,transparent_72%)]" />
      <div className="absolute left-0 right-0 top-1/4 h-px animate-scan bg-gradient-to-r from-transparent via-cyan-300/70 to-transparent" />
    </div>
  );
}
