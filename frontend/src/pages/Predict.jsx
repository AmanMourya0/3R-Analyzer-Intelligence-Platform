import { useState } from 'react'
import { Sparkles } from 'lucide-react'
import { predictTicket } from '../api'
import Card from '../components/Card'
import Badge from '../components/Badge'

export default function Predict() {
  const [desc, setDesc] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handlePredict() {
    if (!desc.trim()) return
    setLoading(true)
    setResult(null)
    setError('')
    try {
      const r = await predictTicket(desc.trim())
      setResult(r.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Prediction failed. Make sure data is loaded.')
    } finally {
      setLoading(false)
    }
  }

  function handleKey(e) {
    if (e.key === 'Enter' && e.ctrlKey) handlePredict()
  }

  return (
    <div className="fade-up" style={{ maxWidth: 860 }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text)' }}>Predict New Ticket</h1>
        <p style={{ fontSize: 13, color: 'var(--text2)', marginTop: 4 }}>Enter a ticket description to find its cluster and similar issues</p>
      </div>

      <Card style={{ marginBottom: 24 }}>
        <div style={{ fontWeight: 600, marginBottom: 10, fontSize: 14 }}>Ticket description</div>
        <textarea
          value={desc}
          onChange={e => setDesc(e.target.value)}
          onKeyDown={handleKey}
          placeholder="e.g. Cannot connect to office VPN after password reset…"
          rows={4}
        />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 12 }}>
          <span style={{ fontSize: 11, color: 'var(--text2)' }}>Ctrl+Enter to submit</span>
          <button
            onClick={handlePredict}
            disabled={loading || !desc.trim()}
            className="btn-primary"
            style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 24px' }}
          >
            <Sparkles size={14} />
            {loading ? 'Analyzing…' : 'Analyze Ticket'}
          </button>
        </div>
      </Card>

      {error && (
        <div style={{
          background: 'var(--red-bg)', border: '1px solid rgba(244,63,94,0.3)',
          borderRadius: 10, padding: '12px 16px', marginBottom: 16,
          color: 'var(--red)', fontSize: 13,
        }}>
          {error}
        </div>
      )}

      {result && (
        <div className="fade-up">
          {/* Result banner */}
          <Card style={{
            marginBottom: 20,
            borderColor: result.is_new_cluster ? 'rgba(124,58,237,0.4)' : 'rgba(34,197,94,0.4)',
            background: result.is_new_cluster ? 'var(--purple-bg)' : 'var(--green-bg)',
          }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
              <span style={{ fontSize: 22, flexShrink: 0 }}>{result.is_new_cluster ? '🆕' : '✅'}</span>
              <div>
                <div style={{ fontWeight: 700, fontSize: 15 }}>
                  {result.is_new_cluster ? 'New cluster created: ' : 'Matched cluster: '}
                  <span style={{ color: 'var(--accent)' }}>{result.predicted_cluster_name}</span>
                </div>
                <div style={{ color: 'var(--text2)', fontSize: 12, marginTop: 4 }}>
                  Similarity score:{' '}
                  <strong style={{ color: scoreColor(result.similarity_score) }}>
                    {result.similarity_score}
                  </strong>
                  &nbsp;·&nbsp;Threshold: {result.threshold_used}
                  &nbsp;·&nbsp;Cluster ID: {result.predicted_cluster_id}
                </div>
              </div>
            </div>
          </Card>

          {/* Suggested resolution */}
          {result.suggested_resolution && (
            <Card style={{ marginBottom: 20, borderColor: 'rgba(15,98,254,0.3)', background: 'var(--accent-bg)' }}>
              <div style={{ fontSize: 11, color: 'var(--text2)', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                💡 Suggested Resolution
              </div>
              <div style={{ fontWeight: 500, fontSize: 14 }}>{result.suggested_resolution}</div>
            </Card>
          )}

          {/* Similar tickets */}
          {result.similar_tickets && result.similar_tickets.length > 0 && (
            <Card>
              <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 14 }}>Similar Tickets</div>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border)' }}>
                      {['Score', 'Ticket ID', 'Description', 'Cluster', 'Resolution'].map(h => (
                        <th key={h} style={{ textAlign: 'left', padding: '7px 10px', color: 'var(--text2)', fontWeight: 500, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.similar_tickets.map((t, i) => (
                      <tr key={i} className="data-row" style={{ borderBottom: '1px solid var(--border)' }}>
                        <td style={td}>
                          <span style={{
                            display: 'inline-block',
                            background: scoreColor(t.similarity_score) + '22',
                            color: scoreColor(t.similarity_score),
                            padding: '2px 10px', borderRadius: 6, fontWeight: 700, fontSize: 12,
                          }}>
                            {t.similarity_score}
                          </span>
                        </td>
                        <td style={td}>
                          <span style={{ fontFamily: 'monospace', fontSize: 11, color: 'var(--accent-h)' }}>{t.ticket_id}</span>
                        </td>
                        <td style={{ ...td, maxWidth: 260 }}>{t.ticket_description}</td>
                        <td style={td}>
                          {t.cluster_name ? <Badge>{t.cluster_name}</Badge> : <span style={{ color: 'var(--text2)' }}>—</span>}
                        </td>
                        <td style={{ ...td, color: 'var(--text2)', maxWidth: 200 }}>{t.resolution || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

const td = { padding: '9px 10px', fontSize: 12 }

function scoreColor(s) {
  if (s >= 0.7) return 'var(--green)'
  if (s >= 0.5) return 'var(--amber)'
  return 'var(--red)'
}
