import { useEffect, useState } from 'react'
import { ChevronDown, ChevronRight, Flag, ExternalLink } from 'lucide-react'
import { getClusters, getCIList, getClusterDetail } from '../api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import ExportMenu from '../components/ExportMenu'
import { useSearchParams, useNavigate } from 'react-router-dom'

// Persist flagged cluster IDs in localStorage
function loadFlagged() {
  try { return new Set(JSON.parse(localStorage.getItem('3r-flagged') || '[]')) }
  catch { return new Set() }
}
function saveFlagged(set) {
  localStorage.setItem('3r-flagged', JSON.stringify([...set]))
}

export default function Clusters() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const initialClusterId = searchParams.get('cluster_id')

  const [clusters, setClusters] = useState([])
  const [ciList, setCiList] = useState([])
  const [selectedCI, setSelectedCI] = useState('All CIs')
  const [expanded, setExpanded] = useState({})
  const [detailMap, setDetailMap] = useState({})
  const [flagged, setFlagged] = useState(loadFlagged)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([getClusters(), getCIList()])
      .then(([cr, cir]) => {
        setClusters(cr.data.clusters || [])
        setCiList(['All CIs', ...(cir.data.ci_list || []).map(c => c.ci_name)])
        
        if (initialClusterId) {
            const cid = parseInt(initialClusterId, 10)
            if (!isNaN(cid)) toggleCluster(cid)
        }
      })
      .catch(() => setError('No data loaded yet. Upload a CSV to get started.'))
      .finally(() => setLoading(false))
  }, [initialClusterId])

  function toggleFlag(e, cid, clusterName, ticketCount) {
    e.stopPropagation()
    setFlagged(prev => {
      const next = new Set(prev)
      if (next.has(cid)) {
        next.delete(cid)
      } else {
        next.add(cid)
      }
      saveFlagged(next)
      const meta = JSON.parse(localStorage.getItem('3r-flagged-meta') || '{}')
      if (!next.has(cid)) {
        delete meta[cid]
      } else {
        meta[cid] = { cluster_id: cid, cluster_name: clusterName, ticket_count: ticketCount }
      }
      localStorage.setItem('3r-flagged-meta', JSON.stringify(meta))
      return next
    })
  }

  async function toggleCluster(cid) {
    const isOpen = !expanded[cid]
    setExpanded(prev => ({ ...prev, [cid]: isOpen }))
    if (isOpen && !detailMap[cid]) {
      const r = await getClusterDetail(cid)
      setDetailMap(prev => ({ ...prev, [cid]: r.data }))
    }
  }

  function handleCIChange(ci) {
    setSelectedCI(ci)
    setExpanded({})
  }

  if (error) return <Empty msg={error} />
  if (loading) return <Loader />

  const visibleClusters = selectedCI === 'All CIs'
    ? clusters
    : clusters.filter(c => (c.ci_names || []).includes(selectedCI))

  return (
    <div className="fade-up">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text)' }}>Ticket Clusters</h1>
          <p style={{ fontSize: 13, color: 'var(--text2)', marginTop: 4 }}>
            {selectedCI === 'All CIs'
              ? `${clusters.length} clusters found`
              : `${visibleClusters.length} clusters for ${selectedCI}`}
            {flagged.size > 0 && (
              <span style={{ marginLeft: 10, color: 'var(--red)', fontWeight: 600 }}>
                · {flagged.size} problem {flagged.size === 1 ? 'cluster' : 'clusters'} flagged
              </span>
            )}
          </p>
        </div>
        <select value={selectedCI} onChange={e => handleCIChange(e.target.value)} style={selectStyle}>
          {ciList.map(ci => <option key={ci} value={ci}>{ci}</option>)}
        </select>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {visibleClusters.length === 0
          ? <Empty msg="No clusters found for the selected CI." />
          : visibleClusters.map(c => {
          const isOpen = expanded[c.cluster_id]
          const isFlagged = flagged.has(c.cluster_id)
          const detail = detailMap[c.cluster_id]

          return (
            <Card key={c.cluster_id} style={{
              padding: 0, overflow: 'hidden',
              border: isFlagged ? '1.5px solid var(--red)' : '1px solid var(--border)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '14px 20px' }}>
                <button
                  onClick={e => toggleFlag(e, c.cluster_id, c.cluster_name, c.ticket_count)}
                  title={isFlagged ? 'Remove problem flag' : 'Flag as problem cluster'}
                  style={{
                    background: isFlagged ? 'var(--red-bg)' : 'transparent',
                    border: isFlagged ? '1px solid var(--red)' : '1px solid var(--border)',
                    borderRadius: 6, padding: '4px 6px', cursor: 'pointer',
                    display: 'flex', alignItems: 'center', flexShrink: 0,
                    transition: 'all 0.15s',
                  }}
                >
                  <Flag size={13} color={isFlagged ? 'var(--red)' : 'var(--text3)'} fill={isFlagged ? 'var(--red)' : 'none'} />
                </button>

                <button
                  onClick={() => toggleCluster(c.cluster_id)}
                  style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1, background: 'transparent', border: 'none', color: 'var(--text)', cursor: 'pointer', textAlign: 'left', fontFamily: 'inherit', minWidth: 0 }}
                >
                  {isOpen
                    ? <ChevronDown size={16} color="var(--accent)" />
                    : <ChevronRight size={16} color="var(--text2)" />}
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: isFlagged ? 'var(--red)' : 'var(--green)', flexShrink: 0 }} />
                  <span style={{ fontWeight: 600, fontSize: 14, flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {c.cluster_name}
                  </span>
                  {c.ci_names && c.ci_names.length > 0 && (
                    <span style={{ fontSize: 11, color: 'var(--text2)', flexShrink: 0, marginRight: 4 }}>
                      {c.ci_names.slice(0, 2).join(', ')}{c.ci_names.length > 2 ? ` +${c.ci_names.length - 2}` : ''}
                    </span>
                  )}
                  <Badge color={c.three_r_category === 'RUNNER' ? 'var(--red)' : c.three_r_category === 'REPEATER' ? 'var(--amber)' : c.three_r_category === 'RARE' ? 'var(--purple)' : 'var(--text2)'}>{c.three_r_category || 'UNCLASSIFIED'}</Badge>
                  <Badge color={isFlagged ? 'var(--red)' : 'var(--accent)'}>{c.ticket_count} tickets</Badge>
                </button>
              </div>

              {isOpen && (
                <div style={{ borderTop: '1px solid var(--border)', padding: '20px' }}>
                  {!detail ? (
                    <div style={{ color: 'var(--text2)', fontSize: 13 }}>Loading intelligence...</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                      
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
                        <div style={{ background: 'var(--surface2)', padding: 16, borderRadius: 8 }}>
                          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', marginBottom: 8 }}>3R Classification</div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                             <Badge color={detail.three_r_category === 'RUNNER' ? 'var(--red)' : detail.three_r_category === 'REPEATER' ? 'var(--amber)' : detail.three_r_category === 'RARE' ? 'var(--purple)' : 'var(--text2)'}>{detail.three_r_category || 'UNCLASSIFIED'}</Badge>
                             {detail.problem_candidate && <Badge color="var(--red)">PROBLEM CANDIDATE</Badge>}
                          </div>
                          <div style={{ fontSize: 12, color: 'var(--text2)', lineHeight: 1.5 }}>
                            <strong>Why:</strong> {detail.three_r_reason || 'Classification reason not available — re-process to populate.'}
                          </div>
                        </div>

                        <div style={{ background: 'var(--surface2)', padding: 16, borderRadius: 8 }}>
                          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', marginBottom: 8 }}>Pattern Metrics</div>
                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 4px', fontSize: 12 }}>
                            <div style={{ color: 'var(--text2)' }}>Recurrence Score:</div>
                            <div style={{ color: 'var(--text)', fontWeight: 500 }}>{detail.recurrence_score ?? '—'}</div>
                            <div style={{ color: 'var(--text2)' }}>Active Span:</div>
                            <div style={{ color: 'var(--text)', fontWeight: 500 }}>{detail.active_span_days} days</div>
                            <div style={{ color: 'var(--text2)' }}>Velocity:</div>
                            <div style={{ color: 'var(--text)', fontWeight: 500 }}>{detail.velocity !== null ? `${detail.velocity}/day` : '—'}</div>
                            <div style={{ color: 'var(--text2)' }}>Dates:</div>
                            <div style={{ color: 'var(--text)', fontWeight: 500 }}>{detail.first_incident_date || '—'} to {detail.last_incident_date || '—'}</div>
                          </div>
                        </div>

                        <div style={{ background: 'var(--surface2)', padding: 16, borderRadius: 8 }}>
                          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', marginBottom: 8 }}>Operational Context</div>
                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 4px', fontSize: 12 }}>
                            <div style={{ color: 'var(--text2)' }}>Top CI:</div>
                            <div style={{ color: 'var(--text)', fontWeight: 500 }}>{detail.top_configuration_item || '—'}</div>
                            <div style={{ color: 'var(--text2)' }}>Assignment Group:</div>
                            <div style={{ color: 'var(--text)', fontWeight: 500 }}>{detail.top_assignment_group || '—'}</div>
                            <div style={{ color: 'var(--text2)' }}>Top Priority:</div>
                            <div style={{ color: 'var(--text)', fontWeight: 500 }}><PriorityBadge p={detail.top_priority} /></div>
                            <div style={{ color: 'var(--text2)' }}>Region:</div>
                            <div style={{ color: 'var(--text)', fontWeight: 500 }}>{detail.top_region || '—'}</div>
                          </div>
                        </div>
                      </div>

                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text)' }}>Sample Tickets</div>
                          <button 
                            onClick={() => navigate(`/tickets?cluster_id=${c.cluster_id}`)}
                            className="btn-ghost"
                            style={{ fontSize: 12, padding: '4px 8px', display: 'flex', alignItems: 'center', gap: 6 }}
                          >
                            View all {c.ticket_count} tickets <ExternalLink size={12} />
                          </button>
                        </div>
                        <TicketTable tickets={detail.sample_tickets} />
                      </div>

                    </div>
                  )}
                </div>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}

function TicketTable({ tickets }) {
  if (!tickets || tickets.length === 0) return null
  return (
    <div style={{ overflowX: 'auto', border: '1px solid var(--border)', borderRadius: 8 }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)', background: 'var(--surface2)' }}>
            {['ID', 'Short Description', 'CI', 'Group', 'Priority', 'Status', 'Date'].map(h => (
              <th key={h} style={{ textAlign: 'left', padding: '7px 10px', color: 'var(--text3)', fontWeight: 600, fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.05em', whiteSpace: 'nowrap' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tickets.map((t, idx) => (
            <tr key={t.ticket_id} className="data-row" style={{ borderBottom: idx === tickets.length - 1 ? 'none' : '1px solid var(--border)' }}>
              <td style={td}><span style={{ fontFamily: 'monospace', fontSize: 11, color: 'var(--accent-h)' }}>{t.ticket_id}</span></td>
              <td style={{ ...td, maxWidth: 260, fontWeight: 500 }}>{t.short_description}</td>
              <td style={{ ...td, whiteSpace: 'nowrap' }}>{t.ci_name || '—'}</td>
              <td style={{ ...td, whiteSpace: 'nowrap', color: 'var(--text2)' }}>{t.assigned_group || '—'}</td>
              <td style={td}><PriorityBadge p={t.priority} /></td>
              <td style={td}>{t.status || '—'}</td>
              <td style={{ ...td, whiteSpace: 'nowrap', color: 'var(--text2)' }}>{t.created_date || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function PriorityBadge({ p }) {
  const colors = { Critical: 'var(--red)', High: 'var(--amber)', Medium: 'var(--blue)', Low: 'var(--green)' }
  const color = colors[p] || 'var(--text2)'
  return p ? <Badge color={color}>{p}</Badge> : <span style={{ color: 'var(--text2)' }}>—</span>
}

const td = { padding: '8px 10px', fontSize: 12 }

const selectStyle = {
  background: 'var(--surface2)', border: '1px solid var(--border)',
  color: 'var(--text)', padding: '8px 12px', borderRadius: 8, fontSize: 13, cursor: 'pointer',
}

function Loader() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {[1, 2, 3, 4].map(i => (
        <div key={i} className="skeleton" style={{ height: 56, borderRadius: 12 }} />
      ))}
    </div>
  )
}

function Empty({ msg }) {
  return (
    <div style={{ textAlign: 'center', padding: '80px 20px', color: 'var(--text2)' }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>🗂️</div>
      <div style={{ fontSize: 15, fontWeight: 500, color: 'var(--text)', marginBottom: 8 }}>No Clusters</div>
      <div style={{ fontSize: 13 }}>{msg}</div>
    </div>
  )
}
