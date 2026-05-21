import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import api from '../api'

const STATUS_STYLE = {
  PENDING_REVIEW: { background: '#fff5da', color: '#9a5d00' },
  NEEDS_REVIEW: { background: '#fff2f0', color: '#c24134' },
  APPROVED: { background: '#e9f8ef', color: '#16794a' },
  OVERRIDDEN: { background: '#eef1f5', color: '#4f5f75' },
  READY_FOR_REVIEW: { background: '#e8f7f9', color: '#087f8c' },
}

const getErrorMessage = (err, fallback) => {
  const detail = err.response?.data?.detail
  if (Array.isArray(detail)) return detail.map((item) => item.msg).filter(Boolean).join(', ') || fallback
  return detail || fallback
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const user = useSelector((s) => s.auth.user)
  const isProfessor = user?.role === 'PROFESSOR' || user?.role === 'instructor'
  const [stats, setStats] = useState(null)
  const [batches, setBatches] = useState([])
  const [submissions, setSubmissions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [taForm, setTaForm] = useState({ name: '', email: '', password: 'password123' })
  const [taMessage, setTaMessage] = useState('')
  const [tas, setTas] = useState(() => JSON.parse(localStorage.getItem('scriptsense_tas') || '[]'))

  const pendingSubmissions = useMemo(
    () => submissions.filter((item) => item.status === 'PENDING_REVIEW' || item.status === 'NEEDS_REVIEW'),
    [submissions],
  )

  const loadDashboard = async () => {
    setLoading(true)
    setError('')
    try {
      const [statsRes, batchesRes, submissionsRes] = await Promise.all([
        api.get('/dashboard/stats'),
        api.get('/batches'),
        api.get('/submissions'),
      ])
      setStats(statsRes.data)
      setBatches(batchesRes.data)
      setSubmissions(submissionsRes.data)
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load dashboard'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadDashboard() }, [])

  const handleAddTa = async (e) => {
    e.preventDefault()
    setTaMessage('')
    try {
      await api.post('/auth/signup', { ...taForm, role: 'TA' })
      const nextTas = [{ name: taForm.name, email: taForm.email }, ...tas.filter((ta) => ta.email !== taForm.email)]
      setTas(nextTas)
      localStorage.setItem('scriptsense_tas', JSON.stringify(nextTas))
      setTaMessage('TA account created')
      setTaForm({ name: '', email: '', password: 'password123' })
    } catch (err) {
      setTaMessage(getErrorMessage(err, 'Failed to add TA'))
    }
  }

  return (
    <main style={S.page}>
      <div style={S.header}>
        <div>
          <p style={S.eyebrow}>{isProfessor ? 'Professor workspace' : 'TA workspace'}</p>
          <h2 style={S.h2}>{isProfessor ? 'Script batches' : 'Assigned scripts'}</h2>
        </div>
        {isProfessor && (
          <button style={S.primaryBtn} onClick={() => navigate('/upload/new')}>Upload PDFs and rubric</button>
        )}
      </div>

      {error && <p style={S.err}>{error}</p>}

      {loading ? (
        <p style={S.muted}>Loading...</p>
      ) : (
        <>
          <section style={S.statsGrid}>
            <Metric label="Scripts" value={stats?.total_submissions ?? submissions.length} />
            <Metric label="Pending review" value={stats?.pending_review ?? pendingSubmissions.length} />
            <Metric label="Approved" value={stats?.approved ?? 0} />
            <Metric label="Flags" value={stats?.needs_review ?? 0} />
          </section>

          {isProfessor && (
            <section style={S.twoCol}>
              <div style={S.panel}>
                <div style={S.panelHead}>
                  <h3 style={S.h3}>Batches</h3>
                  <button style={S.secondaryBtn} onClick={() => navigate('/upload/new')}>New upload</button>
                </div>
                {batches.length === 0 ? (
                  <p style={S.muted}>No batches yet.</p>
                ) : (
                  <div style={S.stack}>
                    {batches.map((batch) => (
                      <div key={batch.id} style={S.batchRow}>
                        <div>
                          <p style={S.itemTitle}>{batch.title}</p>
                          <p style={S.itemSub}>{batch.course} | {batch.processed_submissions}/{batch.total_submissions} processed</p>
                        </div>
                        <span style={{ ...S.badge, ...(STATUS_STYLE[batch.status] ?? STATUS_STYLE.READY_FOR_REVIEW) }}>{batch.status}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div style={S.panel}>
                <h3 style={S.h3}>Add TA</h3>
                <form onSubmit={handleAddTa} style={S.taForm}>
                  <input style={S.input} placeholder="TA name" required value={taForm.name} onChange={(e) => setTaForm({ ...taForm, name: e.target.value })} />
                  <input style={S.input} placeholder="TA email" type="email" required value={taForm.email} onChange={(e) => setTaForm({ ...taForm, email: e.target.value })} />
                  <input style={S.input} placeholder="Temporary password" required minLength={8} value={taForm.password} onChange={(e) => setTaForm({ ...taForm, password: e.target.value })} />
                  <button style={S.primaryBtn} type="submit">Create TA account</button>
                </form>
                {taMessage && <p style={taMessage.includes('created') ? S.ok : S.err}>{taMessage}</p>}
                {tas.length > 0 && (
                  <div style={S.roster}>
                    {tas.map((ta) => <span key={ta.email} style={S.pill}>{ta.name} | {ta.email}</span>)}
                  </div>
                )}
              </div>
            </section>
          )}

          <section style={S.panel}>
            <div style={S.panelHead}>
              <h3 style={S.h3}>{isProfessor ? 'Submission queue' : 'Scripts to evaluate'}</h3>
              <button style={S.secondaryBtn} onClick={loadDashboard}>Refresh</button>
            </div>
            {submissions.length === 0 ? (
              <p style={S.muted}>No scripts uploaded yet.</p>
            ) : (
              <div style={S.table}>
                {submissions.map((submission) => (
                  <article key={submission.id} style={S.submissionRow}>
                    <div>
                      <p style={S.itemTitle}>{submission.student_name}</p>
                      <p style={S.itemSub}>{submission.original_filename} | Batch #{submission.batch_id}</p>
                    </div>
                    <div style={S.scoreBlock}>
                      <span style={S.score}>{submission.ai_score} / {submission.max_score}</span>
                      <span style={S.itemSub}>{Math.round((submission.confidence ?? 0) * 100)}% confidence</span>
                    </div>
                    <span style={{ ...S.badge, ...(STATUS_STYLE[submission.status] ?? STATUS_STYLE.PENDING_REVIEW) }}>{submission.status}</span>
                    <a style={S.linkBtn} href={`/api/submissions/${submission.id}/file`} target="_blank" rel="noreferrer">Open PDF</a>
                    <button style={S.primaryBtn} onClick={() => navigate(`/review/${submission.id}`)}>Evaluate</button>
                  </article>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </main>
  )
}

function Metric({ label, value }) {
  return (
    <div style={S.metric}>
      <p style={S.metricLabel}>{label}</p>
      <p style={S.metricValue}>{value}</p>
    </div>
  )
}

const S = {
  page: { maxWidth: 1180, margin: '36px auto', padding: '0 24px' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 18, marginBottom: 24, flexWrap: 'wrap' },
  eyebrow: { color: '#087f8c', fontSize: 12, fontWeight: 850, textTransform: 'uppercase', letterSpacing: 0, marginBottom: 4 },
  h2: { color: '#172033', fontSize: 30, fontWeight: 850, letterSpacing: 0 },
  h3: { color: '#172033', fontSize: 18, fontWeight: 850 },
  muted: { color: '#68778f', fontSize: 14 },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 14, marginBottom: 18 },
  metric: { background: '#ffffff', border: '1px solid #d9e1ec', borderRadius: 8, padding: 18, boxShadow: '0 12px 28px rgba(31,42,68,.06)' },
  metricLabel: { color: '#68778f', fontSize: 12, fontWeight: 850, textTransform: 'uppercase', letterSpacing: 0 },
  metricValue: { color: '#172033', fontSize: 30, fontWeight: 900, marginTop: 8 },
  twoCol: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(420px, 100%), 1fr))', gap: 18, marginBottom: 18 },
  panel: { background: '#ffffff', border: '1px solid #d9e1ec', borderRadius: 8, padding: 20, boxShadow: '0 16px 36px rgba(31,42,68,.07)', marginBottom: 18 },
  panelHead: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginBottom: 16, flexWrap: 'wrap' },
  stack: { display: 'flex', flexDirection: 'column', gap: 10 },
  batchRow: { display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center', border: '1px solid #edf1f6', borderRadius: 8, padding: 14 },
  table: { display: 'flex', flexDirection: 'column', gap: 10 },
  submissionRow: { display: 'flex', gap: 12, alignItems: 'center', border: '1px solid #edf1f6', borderRadius: 8, padding: 14, flexWrap: 'wrap' },
  itemTitle: { color: '#172033', fontWeight: 850, fontSize: 15 },
  itemSub: { color: '#68778f', fontSize: 13, marginTop: 4 },
  scoreBlock: { display: 'flex', flexDirection: 'column', gap: 2 },
  score: { color: '#172033', fontWeight: 850, fontSize: 15 },
  badge: { fontSize: 11, padding: '6px 9px', borderRadius: 999, width: 'fit-content', textTransform: 'uppercase', fontWeight: 850, letterSpacing: 0 },
  primaryBtn: { padding: '10px 14px', borderRadius: 8, background: '#087f8c', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 850, fontSize: 13, textAlign: 'center' },
  secondaryBtn: { padding: '10px 14px', borderRadius: 8, background: '#ffffff', color: '#263247', border: '1px solid #cfd8e6', cursor: 'pointer', fontWeight: 850, fontSize: 13 },
  linkBtn: { padding: '10px 14px', borderRadius: 8, background: '#ffffff', color: '#087f8c', border: '1px solid #bde8ed', cursor: 'pointer', fontWeight: 850, fontSize: 13, textAlign: 'center' },
  taForm: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10, marginTop: 14 },
  input: { padding: '11px 13px', borderRadius: 8, border: '1px solid #cfd8e6', background: '#f8fafc', color: '#172033', fontSize: 14, width: '100%', outline: 'none' },
  roster: { display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 14 },
  pill: { background: '#e8f7f9', color: '#087f8c', borderRadius: 999, padding: '7px 10px', fontSize: 12, fontWeight: 850 },
  ok: { color: '#16794a', background: '#e9f8ef', border: '1px solid #bfe7cf', borderRadius: 8, fontSize: 13, marginTop: 12, padding: '10px 12px' },
  err: { color: '#c24134', background: '#fff2f0', border: '1px solid #ffd1ca', borderRadius: 8, fontSize: 13, marginBottom: 14, padding: '10px 12px' },
}
