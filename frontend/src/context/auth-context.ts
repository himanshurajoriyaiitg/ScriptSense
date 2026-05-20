import { createContext } from 'react'
import type { AuthProvider, LoginPayload, SessionUser, SignupPayload, UserRole } from '../types/auth'

export type AuthResult = {
  ok: boolean
  message?: string
  user?: SessionUser
}

export type AuthContextValue = {
  user: SessionUser | null
  login: (payload: LoginPayload) => Promise<AuthResult>
  signup: (payload: SignupPayload) => Promise<AuthResult>
  socialLogin: (provider: Exclude<AuthProvider, 'email'>, role: UserRole) => Promise<AuthResult>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)
