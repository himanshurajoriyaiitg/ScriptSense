import type { ReactNode } from 'react'
import { useMemo, useState } from 'react'
import {
  clearSession,
  createUser,
  findUserByEmail,
  getSession,
  saveSession,
  updateUser,
  upsertSocialUser,
} from '../lib/authStorage'
import { AuthContext, type AuthContextValue } from './auth-context'
import type { SessionUser } from '../types/auth'

const wait = (milliseconds = 420) => new Promise((resolve) => window.setTimeout(resolve, milliseconds))

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(() => getSession())

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      async login(payload) {
        await wait()

        const storedUser = findUserByEmail(payload.email)
        if (!storedUser || storedUser.password !== payload.password) {
          return {
            ok: false,
            message: 'Those credentials do not match a ScriptSense user.',
          }
        }

        const nextUser = updateUser({
          ...storedUser,
          lastLoginAt: new Date().toISOString(),
        })
        const sessionUser = saveSession(nextUser)
        setUser(sessionUser)

        return { ok: true, user: sessionUser }
      },
      async signup(payload) {
        await wait()

        if (findUserByEmail(payload.email)) {
          return {
            ok: false,
            message: 'An account with that email already exists.',
          }
        }

        const storedUser = createUser(payload)
        const sessionUser = saveSession(storedUser)
        setUser(sessionUser)

        return { ok: true, user: sessionUser }
      },
      async socialLogin(provider, role) {
        await wait(320)

        const storedUser = upsertSocialUser({ provider, role })
        const sessionUser = saveSession(storedUser)
        setUser(sessionUser)

        return { ok: true, user: sessionUser }
      },
      logout() {
        clearSession()
        setUser(null)
      },
    }),
    [user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
