export type UserRole = 'PROFESSOR' | 'TA'

export type AuthProvider = 'email' | 'Google' | 'Facebook' | 'Apple ID'

export type StoredUser = {
  id: string
  name: string
  email: string
  password: string
  role: UserRole
  provider: AuthProvider
  createdAt: string
  lastLoginAt: string
}

export type SessionUser = Omit<StoredUser, 'password'>

export type LoginPayload = {
  email: string
  password: string
  role: UserRole
}

export type SignupPayload = LoginPayload & {
  name: string
}
