import { useEffect, useState } from 'react'
import { ArrowLeft, Users, Calendar } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, ResponsiveContainer,
} from 'recharts'
import { getGroupList, getGroupClusters, getTickets } from '../api'
import Card from '../components/Card'
import StatCard from '../components/StatCard'
import Badge from '../components/Badge'

const TOOLTIP_STYLE = {
  background: 'var(--surface)', border: '1px solid var(--border)',
  color: 'var(--text)', borderRadius: 8, fontSize: 12,
}

// Custom Y-axis tick — full name, right-aligned, no wrapping
function CustomYTick({ x, y, payload }) {
  const name = payload?.value || ''
  return (
    <g transform={`translate(${x},${y})`}>
      <text x={0} y={0} dy={4} textAnchor="end" fill="var(--text)" fontSize={11}
        style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
        {name}
      </text>
    </g>
  )
}

export default function AssignedGroup() {
  const [groupList, setGroupList] = useState([])
  const [selected, setSelected] = useState(null)
  const [detail, setDetail] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getGroupList()
      .then(r => setGroupList(r.data.group_list || []))
      .catch(() => setError('No data loaded yet. Upload a CSV to get started.'))
      .finally(() => setLoading(false))
  }, [])

  async function selectGroup(groupName) {
    setSelected(groupName)
    setDetail(null)
    const r = await getGroupClusters(groupName)
    setDetail(r.data)
  }

  if (error) return <Empty msg={error} />
  if (loading) return <Loader />

  if (selected && detail) {
    return <GroupDetail detail={detail} onBack={() => { setSelected(null); setDetail(null) }} />
  }

  const filtered = groupList.filter(g =>
    g.group_name.toLowerCase().includes(search.toLowerCase())
  )

  const barData = [...groupList]
    .sort((a, b) => b.total_tickets - a.total_tickets)
    .slice(0, 15)
    .map(g => ({
      name: g.group_name,
      Recurring: g.recurring_tickets || 0,
      Unique: (g.total_tickets || 0) - (g.recurring_tickets || 0),
    }))

  return (
    <div className="fade-up">
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text)' }}>Assigned Group Analysis</h1>
        <p style={{ fontSize: 13, color: 'var(--text2)', marginTop: 4 }}>{groupList.length} assigned groups</p>
      </div>

      {barData.length > 0 && (
        <Card style={{ marginBottom: 24 }}>
          <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 14 }}>Top Groups — Recurring vs Unique</div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={barData} margin={{ bottom: 60 }}>
              <XAxis dataKey="name" stroke="transparent" tick={{ fill: 'var(--text2)', fontSize: 10 }} angle={-30} textAnchor="end" height={70} />
              <YAxis stroke="transparent" tick={{ fill: 'var(--text2)', fontSize: 11 }} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Bar dataKey="Recurring" stackId="a" fill="var(--accent)" />
              <Bar dataKey="Unique" stackId="a" fill="var(--purple)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ fontWeight: 600, fontSize: 14 }}>All Groups ({filtered.length})</div>
        <input placeholder="Search group…" value={search} onChange={e => setSearch(e.target.value)} style={{ width: 220 }} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
        {filtered.map(g => (
          <Card key={g.group_name} hover style={{ cursor: 'pointer' }} onClick={() => selectGroup(g.group_name)}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: 'var(--purple-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Users size={16} color="var(--purple)" />
              </div>
              <div style={{ fontWeight: 600, fontSize: 13, flex: 1, lineHeight: 1.3 }}>{g.group_name}</div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 14 }}>
              <MiniStat label="Total" value={g.total_tickets} />
              <MiniStat label="Recurring" value={`${g.recurring_percentage || 0}%`} color="var(--green)" />
              <MiniStat label="Clusters" value={g.cluster_count} color="var(--accent)" />
              <MiniStat label="Unique" value={(g.total_tickets || 0) - (g.recurring_tickets || 0)} color="var(--amber)" />
            </div>
            <div style={{ background: 'linear-gradient(135deg, var(--purple), var(--accent))', color: '#fff', padding: '7px', borderRadius: 8, textAlign: 'center', fontSize: 12, fontWeight: 600 }}>
              View Clusters →
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}

function GroupDetail({ detail, onBack }) {
  const [expanded, setExpanded] = useState({})
  const [ticketMap, setTicketMap] = useState({})
  const [dateFilters, setDateFilters] = useState({})

  async function toggleCluster(cid) {
    const isOpen = !expanded[cid]
    setExpanded(prev => ({ ...prev, [cid]: isOpen }))
    if (isOpen && !ticketMap[cid]) {
      const r = await getTickets({ cluster_id: cid, assigned_group: detail.group_name, limit: 1000 })
      setTicketMap(prev => ({ ...prev, [cid]: r.data.tickets || [] }))
    }
  }

  function setDateFilter(cid, key, val) {
    setDateFilters(prev => ({ ...prev, [cid]: { ...(prev[cid] || {}), [key]: val } }))
  }

  function clearDateFilter(cid) {
    setDateFilters(prev => ({ ...prev, [cid]: { from: '', to: '' } }))
  }

  function filterByDate(tickets, cid) {
    const f = dateFilters[cid] || {}
    if (!f.from && !f.to) return tickets
    return tickets.filter(t => {
      const d = (t.created_date || '').slice(0, 10)
      if (!d) return true
      if (f.from && d < f.from) return false
      if (f.to   && d > f.to)   return false
      return true
    })
  }

  const recurring = detail.recurring_tickets ?? 0
  const recurringPct = detail.recurring_percentage ?? 0
  const barData = (detail.clusters || []).filter(c => c.cluster_id !== -1 && c.ticket_count > 0)
    .map(c => ({ name: c.cluster_name, tickets: c.ticket_count }))
  const pieData = [{ name: 'Recurring', value: recurring }, { name: 'Unique', value: detail.total_tickets - recurring }]

  return (
    <div className="fade-up">
      <button onClick={onBack} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'transparent', border: 'none', color: 'var(--accent)', cursor: 'pointer', marginBottom: 20, fontSize: 13, fontFamily: 'inherit' }}>
        <ArrowLeft size={15} /> Back to All Groups
      </button>

      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text)' }}>{detail.group_name}</h1>
        <p style={{ fontSize: 13, color: 'var(--text2)', marginTop: 4 }}>{detail.total_tickets} tickets · {barData.length} clusters</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 24 }}>
        <StatCard label="Total Tickets" value={detail.total_tickets} />
        <StatCard label="Clusters" value={barData.length} color="var(--purple)" bg="var(--purple-bg)" />
        <StatCard label="Recurring" value={`${recurringPct}%`} color="var(--green)" bg="var(--green-bg)" />
        <StatCard label="Unique" value={detail.total_tickets - recurring} color="var(--amber)" bg="var(--amber-bg)" />
      </div>

      {barData.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
          <Card style={{ overflow: 'hidden' }}>
            <div style={{ fontWeight: 600, marginBottom: 12, fontSize: 14 }}>Cluster Distribution</div>
            <div style={{ overflowY: 'auto', maxHeight: 340 }}>
              <div style={{ height: Math.max(200, barData.length * 30) }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barData} layout="vertical" margin={{ left: 4, right: 20, top: 2, bottom: 2 }} barSize={14}>
                    <XAxis type="number" stroke="transparent" tick={{ fill: 'var(--text2)', fontSize: 11 }} />
                    <YAxis type="category" dataKey="name" width={190} stroke="transparent" tick={<CustomYTick />} />
                    <Tooltip
                      contentStyle={TOOLTIP_STYLE}
                      formatter={val => [val, 'Tickets']}
                    />
                    <Bar dataKey="tickets" fill="url(#grpGrad)" radius={[0, 5, 5, 0]} />
                    <defs>
                      <linearGradient id="grpGrad" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="var(--purple)" />
                        <stop offset="100%" stopColor="var(--accent)" />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Card>
          <Card>
            <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 14 }}>Recurring vs Unique</div>
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="value" paddingAngle={3}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={{ stroke: 'var(--border2)' }}>
                  <Cell fill="var(--purple)" />
                  <Cell fill="var(--accent)" />
                </Pie>
                <Tooltip contentStyle={TOOLTIP_STYLE} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </div>
      )}

      <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 14 }}>Tickets by Cluster</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {(detail.clusters || []).filter(c => c.ticket_count > 0).map(c => {
          const isNoise = c.cluster_id === -1
          const isOpen = expanded[c.cluster_id]
          const allTickets = ticketMap[c.cluster_id] || c.tickets || []
          const df = dateFilters[c.cluster_id] || {}
          const tickets = filterByDate(allTickets, c.cluster_id)

          return (
            <Card key={c.cluster_id} style={{ padding: 0, overflow: 'hidden' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '13px 20px', flexWrap: 'wrap' }}>
                <button
                  onClick={() => toggleCluster(c.cluster_id)}
                  style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1, background: 'transparent', border: 'none', color: 'var(--text)', cursor: 'pointer', textAlign: 'left', fontFamily: 'inherit', minWidth: 0 }}
                >
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: isNoise ? 'var(--amber)' : 'var(--purple)', flexShrink: 0 }} />
                  <span style={{ fontWeight: 600, fontSize: 13, flex: 1 }}>{c.cluster_name}</span>
                  <Badge color={isNoise ? 'var(--amber)' : 'var(--purple)'}>
                    {isOpen && (df.from || df.to) ? `${tickets.length}/` : ''}{c.ticket_count} tickets
                  </Badge>
                </button>

                {isOpen && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5, flexShrink: 0 }}>
                    <Calendar size={13} color="var(--text2)" />
                    <span style={{ fontSize: 11, color: 'var(--text3)' }}>From</span>
                    <input type="date" value={df.from || ''} onChange={e => setDateFilter(c.cluster_id, 'from', e.target.value)} style={dateInputStyle} />
                    <span style={{ fontSize: 11, color: 'var(--text3)' }}>To</span>
                    <input type="date" value={df.to || ''} onChange={e => setDateFilter(c.cluster_id, 'to', e.target.value)} style={dateInputStyle} />
                    {(df.from || df.to) && (
                      <button onClick={() => clearDateFilter(c.cluster_id)} style={{ fontSize: 11, background: 'none', border: 'none', color: 'var(--text3)', cursor: 'pointer', padding: '0 2px', fontFamily: 'inherit' }}>✕</button>
                    )}
                  </div>
                )}
              </div>

              {isOpen && (
                <div style={{ borderTop: '1px solid var(--border)', padding: '0 20px 16px' }}>
                  {allTickets.length === 0
                    ? <div style={{ color: 'var(--text2)', padding: '14px 0', fontSize: 13 }}>Loading…</div>
                    : tickets.length === 0
                      ? <div style={{ color: 'var(--text2)', padding: '14px 0', fontSize: 13 }}>No tickets in this date range.</div>
                      : <MiniTable tickets={tickets} />
                  }
                </div>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}

function MiniTable({ tickets }) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 12 }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)' }}>
            {['ID', 'Short Description', 'CI', 'Priority', 'Status', 'Date', 'Resolution'].map(h => (
              <th key={h} style={{ textAlign: 'left', padding: '7px 10px', color: 'var(--text2)', fontWeight: 500, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em', whiteSpace: 'nowrap' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tickets.map((t, i) => (
            <tr key={t.ticket_id || i} className="data-row" style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={td}><span style={{ fontFamily: 'monospace', fontSize: 11, color: 'var(--accent-h)' }}>{t.ticket_id}</span></td>
              <td style={{ ...td, maxWidth: 260 }}>{t.short_description}</td>
              <td style={{ ...td, whiteSpace: 'nowrap', color: 'var(--text2)' }}>{t.ci_name || '—'}</td>
              <td style={td}><PriorityBadge p={t.priority} /></td>
              <td style={td}>{t.status || '—'}</td>
              <td style={{ ...td, whiteSpace: 'nowrap', color: 'var(--text2)' }}>{t.created_date || '—'}</td>
              <td style={{ ...td, color: 'var(--text2)', maxWidth: 200 }}>{t.resolution || '—'}</td>
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

function MiniStat({ label, value, color }) {
  return (
    <div style={{ background: 'var(--bg)', borderRadius: 8, padding: '8px 12px' }}>
      <div style={{ fontSize: 16, fontWeight: 700, color: color || 'var(--text)' }}>{value}</div>
      <div style={{ fontSize: 11, color: 'var(--text2)' }}>{label}</div>
    </div>
  )
}

const td = { padding: '8px 10px', fontSize: 12 }

const dateInputStyle = {
  background: 'var(--surface2)', border: '1px solid var(--border)',
  color: 'var(--text)', padding: '3px 7px', borderRadius: 6,
  fontSize: 11, fontFamily: 'inherit', outline: 'none', cursor: 'pointer',
}

function Loader() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
      {[1, 2, 3, 4, 5, 6].map(i => <div key={i} className="skeleton" style={{ height: 160, borderRadius: 12 }} />)}
    </div>
  )
}

function Empty({ msg }) {
  return (
    <div style={{ textAlign: 'center', padding: '80px 20px', color: 'var(--text2)' }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>👥</div>
      <div style={{ fontSize: 15, fontWeight: 500, color: 'var(--text)', marginBottom: 8 }}>No Group Data</div>
      <div style={{ fontSize: 13 }}>{msg}</div>
    </div>
  )
}
