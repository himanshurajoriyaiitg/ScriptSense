import { Link, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { logout } from '../store'

export default function Navbar() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const user = useSelector((s) => s.auth.user)
  const displayName = user?.full_name || user?.name || user?.email
  const displayRole = user?.role ? String(user.role).toLowerCase() : ''

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <nav style={S.nav}>
      <Link to="/" style={S.brand}>
        <span style={S.mark}>S</span>
        <span>ScriptSense</span>
      </Link>
      <div style={S.right}>
        <span style={S.user}>{displayName} | {displayRole}</span>
        <button onClick={handleLogout} style={S.btn}>Sign out</button>
      </div>
    </nav>
  )
}

const S = {
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '14px 32px',
    background: 'rgba(255,255,255,.92)',
    borderBottom: '1px solid #d9e1ec',
    boxShadow: '0 12px 30px rgba(31,42,68,.07)',
    position: 'sticky',
    top: 0,
    zIndex: 20,
    backdropFilter: 'blur(10px)',
  },
  brand: { display: 'flex', alignItems: 'center', gap: 10, color: '#172033', fontWeight: 800, fontSize: 19 },
  mark: {
    width: 34,
    height: 34,
    borderRadius: 8,
    display: 'grid',
    placeItems: 'center',
    background: '#087f8c',
    color: '#fff',
    fontSize: 17,
    boxShadow: '0 8px 18px rgba(8,127,140,.22)',
  },
  right: { display: 'flex', gap: 14, alignItems: 'center' },
  user: { fontSize: 13, color: '#58657a', textTransform: 'capitalize' },
  btn: {
    background: '#ffffff',
    color: '#263247',
    border: '1px solid #cfd8e6',
    padding: '8px 15px',
    borderRadius: 8,
    cursor: 'pointer',
    fontSize: 13,
    fontWeight: 700,
    boxShadow: '0 4px 12px rgba(31,42,68,.06)',
  },
}
