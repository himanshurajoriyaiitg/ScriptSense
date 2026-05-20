import type { AuthProvider, SessionUser, StoredUser, UserRole } from '../types/auth'

const USERS_KEY = 'scriptsense.users'
const SESSION_KEY = 'scriptsense.session'

const seededUsers: StoredUser[] = [
  {
    id: 'seed-professor',
    name: 'Dr. Aanya Mehta',
    email: 'professor@scriptsense.ai',
    password: 'scriptsense123',
    role: 'PROFESSOR',
    provider: 'email',
    createdAt: '2026-05-15T00:00:00.000Z',
    lastLoginAt: '2026-05-15T00:00:00.000Z',
  },
  {
    id: 'seed-ta',
    name: 'Ravi Narang',
    email: 'ta@scriptsense.ai',
    password: 'scriptsense123',
    role: 'TA',
    provider: 'email',
    createdAt: '2026-05-15T00:00:00.000Z',
    lastLoginAt: '2026-05-15T00:00:00.000Z',
  },
]

const canUseStorage = () => typeof window !== 'undefined' && Boolean(window.localStorage)

const normalizeEmail = (email: string) => email.trim().toLowerCase()

const createId = () => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }

  return `user-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

const toSessionUser = (user: StoredUser): SessionUser => ({
  id: user.id,
  name: user.name,
  email: user.email,
  role: user.role,
  provider: user.provider,
  createdAt: user.createdAt,
  lastLoginAt: user.lastLoginAt,
})

const readStoredUsers = (): StoredUser[] => {
  if (!canUseStorage()) {
    return seededUsers
  }

  try {
    const value = window.localStorage.getItem(USERS_KEY)
    return value ? (JSON.parse(value) as StoredUser[]) : []
  } catch {
    return []
  }
}

const writeStoredUsers = (users: StoredUser[]) => {
  if (canUseStorage()) {
    window.localStorage.setItem(USERS_KEY, JSON.stringify(users))
  }
}

export const getUsers = () => {
  const storedUsers = readStoredUsers()
  const normalizedStoredEmails = new Set(storedUsers.map((user) => normalizeEmail(user.email)))
  const missingSeeds = seededUsers.filter((user) => !normalizedStoredEmails.has(user.email))

  return [...storedUsers, ...missingSeeds]
}

export const findUserByEmail = (email: string) =>
  getUsers().find((user) => normalizeEmail(user.email) === normalizeEmail(email))

export const createUser = (payload: {
  name: string
  email: string
  password: string
  role: UserRole
  provider?: AuthProvider
}) => {
  const now = new Date().toISOString()
  const user: StoredUser = {
    id: createId(),
    name: payload.name.trim(),
    email: normalizeEmail(payload.email),
    password: payload.password,
    role: payload.role,
    provider: payload.provider ?? 'email',
    createdAt: now,
    lastLoginAt: now,
  }

  writeStoredUsers([user, ...readStoredUsers()])
  return user
}

export const upsertSocialUser = (payload: {
  provider: Exclude<AuthProvider, 'email'>
  role: UserRole
}) => {
  const email = `${payload.provider.toLowerCase().replace(/\s+/g, '-')}.user@scriptsense.ai`
  const existingUser = findUserByEmail(email)
  const now = new Date().toISOString()

  if (existingUser) {
    return updateUser({ ...existingUser, role: payload.role, lastLoginAt: now })
  }

  return createUser({
    name: `${payload.provider} User`,
    email,
    password: '',
    role: payload.role,
    provider: payload.provider,
  })
}

export const updateUser = (user: StoredUser) => {
  const users = readStoredUsers()
  const normalizedEmail = normalizeEmail(user.email)
  const nextUsers = users.some((storedUser) => normalizeEmail(storedUser.email) === normalizedEmail)
    ? users.map((storedUser) => (normalizeEmail(storedUser.email) === normalizedEmail ? user : storedUser))
    : [user, ...users]

  writeStoredUsers(nextUsers)
  return user
}

export const saveSession = (user: StoredUser) => {
  const sessionUser = toSessionUser(user)

  if (canUseStorage()) {
    window.localStorage.setItem(SESSION_KEY, JSON.stringify(sessionUser))
  }

  return sessionUser
}

export const getSession = (): SessionUser | null => {
  if (!canUseStorage()) {
    return null
  }

  try {
    const value = window.localStorage.getItem(SESSION_KEY)
    return value ? (JSON.parse(value) as SessionUser) : null
  } catch {
    return null
  }
}

export const clearSession = () => {
  if (canUseStorage()) {
    window.localStorage.removeItem(SESSION_KEY)
  }
}

export const getDashboardPath = (role: UserRole) => (role === 'PROFESSOR' ? '/professor' : '/ta')
