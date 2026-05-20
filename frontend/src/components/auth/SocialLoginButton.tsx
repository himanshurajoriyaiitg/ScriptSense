import { Apple, Loader2 } from 'lucide-react'
import type { AuthProvider } from '../../types/auth'

type SocialProvider = Exclude<AuthProvider, 'email'>

type SocialLoginButtonProps = {
  provider: SocialProvider
  isLoading: boolean
  onClick: (provider: SocialProvider) => void
}

const providerMarks: Record<SocialProvider, string> = {
  Google: 'G',
  Facebook: 'f',
  'Apple ID': '',
}

export function SocialLoginButton({ provider, isLoading, onClick }: SocialLoginButtonProps) {
  return (
    <button
      className="flex h-11 items-center justify-center gap-2 rounded-md border border-white/10 bg-white/[0.06] px-3 text-sm font-semibold text-slate-100 transition duration-300 hover:-translate-y-0.5 hover:border-cyan-200/40 hover:bg-white/[0.1] focus:outline-none focus:ring-2 focus:ring-cyan-300/60 disabled:pointer-events-none disabled:opacity-60"
      disabled={isLoading}
      onClick={() => onClick(provider)}
      type="button"
    >
      {isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : provider === 'Apple ID' ? (
        <Apple className="h-4 w-4" />
      ) : (
        <span className="grid h-5 w-5 place-items-center rounded-md bg-white text-xs font-black text-slate-950">
          {providerMarks[provider]}
        </span>
      )}
      {provider}
    </button>
  )
}
