import { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { login } from '../store'
import api from '../api'

const getErrorMessage = (err, fallback) => {
  const detail = err.response?.data?.detail
  if (Array.isArray(detail)) return detail.map((item) => item.msg).filter(Boolean).join(', ') || fallback
  return detail || fallback
}

export default function LoginPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { loading, error, token } = useSelector((s) => s.auth)
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ email: '', password: '', full_name: '', role: 'TA' })
  const [signupError, setSignupError] = useState('')
  const [signupLoading, setSignupLoading] = useState(false)

  const isSignup = mode === 'signup'

  useEffect(() => { if (token) navigate('/') }, [token, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSignupError('')
    if (!isSignup) {
      dispatch(login({ email: form.email, password: form.password }))
      return
    }

    setSignupLoading(true)
    try {
      await api.post('/auth/signup', {
        email: form.email,
        password: form.password,
        name: form.full_name,
        role: form.role,
      })
      dispatch(login({ email: form.email, password: form.password }))
    } catch (err) {
      setSignupError(getErrorMessage(err, 'Signup failed'))
    } finally {
      setSignupLoading(false)
    }
  }

  return (
    <div style={S.page}>
      <div style={S.shell}>
        <div style={S.brandPanel}>
          <div style={S.logo}>S</div>
          <h1 style={S.title}>ScriptSense</h1>
          <p style={S.sub}>Assessment review workspace</p>
        </div>

        <form onSubmit={handleSubmit} style={S.form}>
          <div style={S.switcher}>
            <button
              type="button"
              style={mode === 'login' ? S.switchActive : S.switchBtn}
              onClick={() => { setMode('login'); setSignupError('') }}
            >
              Sign in
            </button>
            <button
              type="button"
              style={mode === 'signup' ? S.switchActive : S.switchBtn}
              onClick={() => { setMode('signup'); setSignupError('') }}
            >
              Sign up
            </button>
          </div>
          {isSignup && (
            <div>
              <p style={S.label}>Full name</p>
              <input
                style={S.input}
                type="text"
                placeholder="Your name"
                required
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              />
            </div>
          )}
          <div>
            <p style={S.label}>Email</p>
            <input
              style={S.input}
              type="email"
              placeholder="name@example.com"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <div>
            <p style={S.label}>Password</p>
            <input
              style={S.input}
              type="password"
              placeholder="Enter password"
              required
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>
          {isSignup && (
            <div>
              <p style={S.label}>Role</p>
              <select
                style={S.input}
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
              >
                <option value="TA">TA</option>
                <option value="PROFESSOR">Professor</option>
              </select>
            </div>
          )}
          {(error || signupError) && <p style={S.err}>{signupError || error}</p>}
          <button type="submit" style={S.btn} disabled={loading || signupLoading}>
            {loading || signupLoading ? 'Please wait...' : isSignup ? 'Create account' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}

const S = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    background: 'linear-gradient(135deg, #eef7f8 0%, #f7f8fb 48%, #fff3f0 100%)',
  },
  shell: {
    width: 'min(860px, 100%)',
    minHeight: 460,
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(min(300px, 100%), 1fr))',
    background: '#ffffff',
    border: '1px solid #d9e1ec',
    borderRadius: 8,
    overflow: 'hidden',
    boxShadow: '0 28px 70px rgba(31,42,68,.13)',
  },
  brandPanel: {
    background: '#087f8c',
    color: '#ffffff',
    padding: 42,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  logo: {
    width: 54,
    height: 54,
    display: 'grid',
    placeItems: 'center',
    background: '#ffffff',
    color: '#087f8c',
    borderRadius: 8,
    fontWeight: 900,
    fontSize: 26,
    marginBottom: 24,
  },
  title: { margin: '0 0 8px', fontSize: 36, fontWeight: 850, letterSpacing: 0 },
  sub: { color: '#d9fbff', fontSize: 15, lineHeight: 1.5 },
  form: { display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 18, padding: '44px 48px' },
  switcher: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6, background: '#eef3f7', borderRadius: 8, padding: 5 },
  switchBtn: {
    border: 'none',
    borderRadius: 7,
    background: 'transparent',
    color: '#58657a',
    padding: '9px 12px',
    cursor: 'pointer',
    fontWeight: 800,
  },
  switchActive: {
    border: 'none',
    borderRadius: 7,
    background: '#ffffff',
    color: '#087f8c',
    padding: '9px 12px',
    cursor: 'pointer',
    fontWeight: 850,
    boxShadow: '0 6px 14px rgba(31,42,68,.08)',
  },
  label: { color: '#4f5f75', fontSize: 12, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 0, marginBottom: 7 },
  input: {
    padding: '12px 14px',
    borderRadius: 8,
    border: '1px solid #cfd8e6',
    background: '#f8fafc',
    color: '#172033',
    fontSize: 15,
    width: '100%',
    outline: 'none',
  },
  err: {
    color: '#c24134',
    background: '#fff2f0',
    border: '1px solid #ffd1ca',
    borderRadius: 8,
    fontSize: 13,
    margin: 0,
    padding: '10px 12px',
  },
  btn: {
    padding: '13px 16px',
    borderRadius: 8,
    background: '#087f8c',
    color: '#fff',
    border: 'none',
    fontSize: 15,
    cursor: 'pointer',
    fontWeight: 800,
    boxShadow: '0 12px 22px rgba(8,127,140,.2)',
  },
}
