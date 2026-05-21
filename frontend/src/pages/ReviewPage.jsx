import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api from '../api'

const getErrorMessage = (err, fallback) => {
  const detail = err.response?.data?.detail
  if (Array.isArray(detail)) return detail.map((item) => item.msg).filter(Boolean).join(', ') || fallback
  return detail || fallback
}

export default function ReviewPage() {
  const { examId: submissionId } = useParams()
  const navigate = useNavigate()
  const [submission, setSubmission] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [review, setReview] = useState({ decision: 'APPROVED', final_score: '', final_feedback: '', reviewer_notes: '' })

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const { data } = await api.get(`/submissions/${submissionId}`)
        setSubmission(data)
        setReview({
          decision: data.status === 'NEEDS_REVIEW' ? 'NEEDS_REVIEW' : 'APPROVED',
          final_score: data.final_score ?? data.ai_score ?? '',
          final_feedback: data.final_feedback ?? data.ai_feedback ?? '',
          reviewer_notes: data.reviewer_notes ?? '',
        })
      } catch (err) {
        setError(getErrorMessage(err, 'Failed to load script'))
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [submissionId])

  const submitReview = async (decision = review.decision) => {
    setSaving(true)
    setError('')
    try {
      await api.patch(`/submissions/${submissionId}/review`, {
        decision,
        final_score: review.final_score === '' ? null : Number(review.final_score),
        final_feedback: review.final_feedback || null,
        reviewer_notes: review.reviewer_notes || null,
      })
      navigate('/')
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to save review'))
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <main style={S.center}><p style={S.muted}>Loading script...</p></main>

  if (!submission) return (
    <main style={S.center}>
      <p style={S.err}>{error || 'Script not found'}</p>
      <button style={S.secondaryBtn} onClick={() => navigate('/')}>Back</button>
    </main>
  )

  return (
    <main style={S.page}>
      <div style={S.header}>
        <div>
          <p style={S.eyebrow}>Script evaluation</p>
          <h2 style={S.h2}>{submission.student_name}</h2>
          <p style={S.muted}>{submission.original_filename} | Batch #{submission.batch_id}</p>
        </div>
        <a style={S.linkBtn} href={`/api/submissions/${submission.id}/file`} target="_blank" rel="noreferrer">Open PDF</a>
      </div>

      {error && <p style={S.err}>{error}</p>}

      <section style={S.summaryGrid}>
        <Metric label="AI score" value={`${submission.ai_score} / ${submission.max_score}`} />
        <Metric label="Confidence" value={`${Math.round((submission.confidence ?? 0) * 100)}%`} />
        <Metric label="Status" value={submission.status} />
      </section>

      <section style={S.split}>
        <div style={S.panel}>
          <h3 style={S.h3}>Extracted answer</h3>
          <pre style={S.pre}>{submission.extracted_text || 'No extracted text available.'}</pre>
        </div>

        <div style={S.panel}>
          <h3 style={S.h3}>Review decision</h3>
          <div style={S.form}>
            <div>
              <p style={S.label}>Decision</p>
              <select style={S.input} value={review.decision} onChange={(e) => setReview({ ...review, decision: e.target.value })}>
                <option value="APPROVED">Approve</option>
                <option value="OVERRIDDEN">Override score</option>
                <option value="NEEDS_REVIEW">Raise flag</option>
              </select>
            </div>
            <div>
              <p style={S.label}>Final score</p>
              <input
                style={S.input}
                type="number"
                min={0}
                max={submission.max_score}
                step={0.5}
                value={review.final_score}
                onChange={(e) => setReview({ ...review, final_score: e.target.value })}
              />
            </div>
            <div>
              <p style={S.label}>Feedback</p>
              <textarea
                style={{ ...S.input, minHeight: 110, resize: 'vertical' }}
                value={review.final_feedback}
                onChange={(e) => setReview({ ...review, final_feedback: e.target.value })}
              />
            </div>
            <div>
              <p style={S.label}>Reviewer notes</p>
              <textarea
                style={{ ...S.input, minHeight: 90, resize: 'vertical' }}
                value={review.reviewer_notes}
                onChange={(e) => setReview({ ...review, reviewer_notes: e.target.value })}
              />
            </div>
          </div>
          <div style={S.actions}>
            <button style={S.secondaryBtn} onClick={() => navigate('/')}>Cancel</button>
            <button style={S.flagBtn} onClick={() => submitReview('NEEDS_REVIEW')} disabled={saving}>Raise flag</button>
            <button style={S.primaryBtn} onClick={() => submitReview()} disabled={saving}>
              {saving ? 'Saving...' : 'Save evaluation'}
            </button>
          </div>
        </div>
      </section>

      <section style={S.panel}>
        <h3 style={S.h3}>AI feedback</h3>
        <p style={S.bodyText}>{submission.ai_feedback || 'No AI feedback available.'}</p>
        {submission.grade_json && <pre style={S.jsonPre}>{JSON.stringify(submission.grade_json, null, 2)}</pre>}
      </section>
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
  page: { maxWidth: 1180, margin: '30px auto', padding: '0 24px' },
  center: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: 12 },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 18, marginBottom: 20, flexWrap: 'wrap' },
  eyebrow: { color: '#087f8c', fontSize: 12, fontWeight: 850, textTransform: 'uppercase', letterSpacing: 0, marginBottom: 4 },
  h2: { color: '#172033', fontSize: 28, lineHeight: 1.2, fontWeight: 850, letterSpacing: 0 },
  h3: { color: '#172033', fontSize: 18, fontWeight: 850, marginBottom: 14 },
  muted: { color: '#68778f', fontSize: 14 },
  summaryGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 14, marginBottom: 18 },
  metric: { background: '#ffffff', border: '1px solid #d9e1ec', borderRadius: 8, padding: 18, boxShadow: '0 12px 28px rgba(31,42,68,.06)' },
  metricLabel: { color: '#68778f', fontSize: 12, fontWeight: 850, textTransform: 'uppercase', letterSpacing: 0 },
  metricValue: { color: '#172033', fontSize: 22, fontWeight: 900, marginTop: 8 },
  split: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(420px, 100%), 1fr))', gap: 18, marginBottom: 18 },
  panel: { background: '#ffffff', borderRadius: 8, border: '1px solid #d9e1ec', padding: 20, boxShadow: '0 18px 42px rgba(31,42,68,.08)' },
  pre: { color: '#263247', background: '#f8fafc', border: '1px solid #edf1f6', borderRadius: 8, padding: 14, whiteSpace: 'pre-wrap', maxHeight: 560, overflow: 'auto', fontSize: 13, lineHeight: 1.65 },
  jsonPre: { color: '#263247', background: '#f8fafc', border: '1px solid #edf1f6', borderRadius: 8, padding: 14, whiteSpace: 'pre-wrap', maxHeight: 280, overflow: 'auto', fontSize: 12, lineHeight: 1.55, marginTop: 14 },
  form: { display: 'flex', flexDirection: 'column', gap: 13 },
  label: { color: '#4f5f75', fontSize: 12, fontWeight: 850, textTransform: 'uppercase', letterSpacing: 0, marginBottom: 7 },
  input: { padding: '12px 14px', borderRadius: 8, border: '1px solid #cfd8e6', background: '#f8fafc', color: '#172033', fontSize: 14, width: '100%', outline: 'none' },
  bodyText: { color: '#263247', fontSize: 14, lineHeight: 1.65 },
  actions: { display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 16, flexWrap: 'wrap' },
  primaryBtn: { padding: '12px 16px', borderRadius: 8, background: '#087f8c', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 850, fontSize: 14 },
  secondaryBtn: { padding: '12px 16px', borderRadius: 8, background: '#ffffff', color: '#263247', border: '1px solid #cfd8e6', cursor: 'pointer', fontWeight: 850, fontSize: 14 },
  flagBtn: { padding: '12px 16px', borderRadius: 8, background: '#c46a00', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 850, fontSize: 14 },
  linkBtn: { padding: '12px 16px', borderRadius: 8, background: '#ffffff', color: '#087f8c', border: '1px solid #bde8ed', cursor: 'pointer', fontWeight: 850, fontSize: 14 },
  err: { color: '#c24134', background: '#fff2f0', border: '1px solid #ffd1ca', borderRadius: 8, fontSize: 13, margin: 0, padding: '10px 12px' },
}
