import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

const SAMPLE_RUBRIC = JSON.stringify({
  title: 'Midterm rubric',
  questions: [
    {
      id: 'q1',
      prompt: 'Explain the solution and justify the result.',
      points: 10,
      criteria: [
        { description: 'Correct method', points: 4 },
        { description: 'Clear reasoning', points: 4 },
        { description: 'Final answer and notation', points: 2 },
      ],
    },
  ],
  total_points: 10,
}, null, 2)

const getErrorMessage = (err, fallback) => {
  const detail = err.response?.data?.detail
  if (Array.isArray(detail)) return detail.map((item) => item.msg).filter(Boolean).join(', ') || fallback
  return detail || fallback
}

export default function UploadPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ title: '', course: '', rubric_json: SAMPLE_RUBRIC })
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (files.length === 0) { setError('Select at least one PDF'); return }

    try {
      JSON.parse(form.rubric_json)
    } catch {
      setError('Rubric must be valid JSON')
      return
    }

    setUploading(true)
    try {
      const fd = new FormData()
      fd.append('title', form.title)
      fd.append('course', form.course)
      fd.append('rubric_json', form.rubric_json)
      files.forEach((file) => fd.append('files', file))
      await api.post('/exams', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      navigate('/')
    } catch (err) {
      setError(getErrorMessage(err, 'Upload failed'))
    } finally {
      setUploading(false)
    }
  }

  return (
    <main style={S.page}>
      <div style={S.header}>
        <p style={S.eyebrow}>Professor upload</p>
        <h2 style={S.h2}>Upload PDFs and rubric</h2>
      </div>

      <form onSubmit={handleSubmit} style={S.section}>
        <div style={S.grid}>
          <div>
            <p style={S.label}>Batch title</p>
            <input
              style={S.input}
              placeholder="Data Structures midterm"
              value={form.title}
              required
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
          </div>
          <div>
            <p style={S.label}>Course</p>
            <input
              style={S.input}
              placeholder="CS201 Data Structures"
              value={form.course}
              required
              onChange={(e) => setForm({ ...form, course: e.target.value })}
            />
          </div>
        </div>

        <div>
          <p style={S.label}>Rubric JSON</p>
          <textarea
            style={{ ...S.input, ...S.textarea }}
            value={form.rubric_json}
            required
            onChange={(e) => setForm({ ...form, rubric_json: e.target.value })}
          />
        </div>

        <div>
          <p style={S.label}>Student PDFs</p>
          <input
            type="file"
            accept="application/pdf"
            multiple
            required
            style={S.fileInput}
            onChange={(e) => setFiles(Array.from(e.target.files || []))}
          />
          {files.length > 0 && (
            <div style={S.fileList}>
              {files.map((file) => <span key={file.name} style={S.filePill}>{file.name}</span>)}
            </div>
          )}
        </div>

        {error && <p style={S.err}>{error}</p>}

        <div style={S.actions}>
          <button type="button" style={S.secondaryBtn} onClick={() => navigate('/')}>Cancel</button>
          <button type="submit" style={S.btn} disabled={uploading}>
            {uploading ? 'Uploading...' : 'Upload batch'}
          </button>
        </div>
      </form>
    </main>
  )
}

const S = {
  page: { maxWidth: 980, margin: '36px auto', padding: '0 24px' },
  header: { marginBottom: 22 },
  eyebrow: { color: '#087f8c', fontSize: 12, fontWeight: 850, textTransform: 'uppercase', letterSpacing: 0, marginBottom: 4 },
  h2: { color: '#172033', fontSize: 28, lineHeight: 1.2, fontWeight: 850, letterSpacing: 0 },
  section: { background: '#ffffff', padding: 24, borderRadius: 8, border: '1px solid #d9e1ec', display: 'flex', flexDirection: 'column', gap: 16, boxShadow: '0 16px 36px rgba(31,42,68,.07)' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(260px, 100%), 1fr))', gap: 14 },
  label: { color: '#263247', fontWeight: 850, fontSize: 12, textTransform: 'uppercase', letterSpacing: 0, marginBottom: 7 },
  input: { padding: '12px 14px', borderRadius: 8, border: '1px solid #cfd8e6', background: '#f8fafc', color: '#172033', fontSize: 14, width: '100%', outline: 'none' },
  textarea: { minHeight: 260, fontFamily: 'ui-monospace, SFMono-Regular, Consolas, monospace', fontSize: 12, lineHeight: 1.55, resize: 'vertical' },
  fileInput: { width: '100%', color: '#4f5f75', background: '#f8fafc', border: '1px dashed #b9c5d6', borderRadius: 8, padding: '14px' },
  fileList: { display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 10 },
  filePill: { background: '#eef3f7', color: '#263247', borderRadius: 999, padding: '7px 10px', fontSize: 12, fontWeight: 850 },
  actions: { display: 'flex', justifyContent: 'flex-end', gap: 10, flexWrap: 'wrap' },
  btn: { padding: '12px 16px', borderRadius: 8, background: '#087f8c', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 850, fontSize: 14 },
  secondaryBtn: { padding: '12px 16px', borderRadius: 8, background: '#ffffff', color: '#263247', border: '1px solid #cfd8e6', cursor: 'pointer', fontWeight: 850, fontSize: 14 },
  err: { color: '#c24134', background: '#fff2f0', border: '1px solid #ffd1ca', borderRadius: 8, fontSize: 13, margin: 0, padding: '10px 12px' },
}
