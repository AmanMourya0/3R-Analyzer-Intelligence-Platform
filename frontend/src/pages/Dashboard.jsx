import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import { Ticket, Layers, TrendingUp, AlertTriangle, Cpu, Users, Activity } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { getDashboard, enrichClusterNames, getEnrichmentStatus } from '../api'
import Card from '../components/Card'
import StatCard from '../components/StatCard'
import Badge from '../components/Badge'
import ExportMenu from '../components/ExportMenu'

const TOOLTIP_STYLE = { background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', borderRadius: 8, fontSize: 12 }
const TICK = { fill: 'var(--text2)', fontSize: 11 }

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [flaggedClusters, setFlaggedClusters] = useState([])
  const [enrichment, setEnrichment] = useState({ status: 'STANDARD', percent: 0 })
  const navigate = useNavigate()

  const pollEnrichment = () => {
    getEnrichmentStatus().then(res => {
      const { naming_status, job } = res.data;
      setEnrichment(prev => {
        if (prev.status === 'AI_ENRICHMENT_RUNNING' && naming_status === 'AI_ENRICHED') {
          getDashboard().then(r => setData(r.data));
        }
        return { status: naming_status, percent: job?.progress_percent || 0 };
      });
      if (naming_status === 'AI_ENRICHMENT_RUNNING') {
        setTimeout(pollEnrichment, 3000);
      }
    }).catch(() => {});
  };

  const handleEnrich = async () => {
    try {
      await enrichClusterNames();
      setEnrichment({ status: 'AI_ENRICHMENT_RUNNING', percent: 0 });
      setTimeout(pollEnrichment, 1000);
    } catch (e) {
      alert("Failed to start enrichment: " + (e.response?.data?.detail || e.message));
    }
  };

  useEffect(() => {
    getDashboard()
      .then(r => setData(r.data))
      .catch(e => {
        const msg = e.response?.data?.detail || 'No data loaded yet. Upload a CSV to get started.'
        setError(msg)
      })
      .finally(() => pollEnrichment())
  }, [])

  // Read flagged clusters from localStorage on every render
  useEffect(() => {
    function readFlagged() {
      try {
        const meta = JSON.parse(localStorage.getItem('3r-flagged-meta') || '{}')
        setFlaggedClusters(Object.values(meta))
      } catch { setFlaggedClusters([]) }
    }
    readFlagged()
    window.addEventListener('focus', readFlagged)
    return () => window.removeEventListener('focus', readFlagged)
  }, [])

  if (error) return <Empty msg={error} />
  if (!data) return <Loader />

  const barData = data.top_clusters.map(c => ({ name: c.cluster_name, tickets: c.ticket_count, id: c.cluster_id }))
  const pieData = [
    { name: 'Runner',   value: data.runner_count },
    { name: 'Repeater', value: data.repeater_count },
    { name: 'Rare',     value: data.rare_count },
  ]

  const mostActive = data.top_clusters[0]
  const highestImpact = data.top_clusters.find(c => c.three_r_category === 'RUNNER') || mostActive

  // Aggregate top CI and Group from the top clusters
  const ciMap = {}
  const groupMap = {}
  data.top_clusters.forEach(c => {
    if (c.top_ci) ciMap[c.top_ci] = (ciMap[c.top_ci] || 0) + c.ticket_count
    if (c.top_group) groupMap[c.top_group] = (groupMap[c.top_group] || 0) + c.ticket_count
  })
  const topCI = Object.entries(ciMap).sort((a,b) => b[1]-a[1])[0]
  const topGroup = Object.entries(groupMap).sort((a,b) => b[1]-a[1])[0]

  return (
    <div className="fade-up" style={{ paddingBottom: 60 }}>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text)' }}>Executive Intelligence</h1>
          <p style={{ fontSize: 13, color: 'var(--text2)', marginTop: 4 }}>Leadership-ready analytics and pattern insights</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {enrichment.status === 'AI_ENRICHMENT_RUNNING' ? (
            <div style={{ fontSize: 13, color: 'var(--text2)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="spinner-small" style={{ width: 12, height: 12, border: '2px solid var(--accent)', borderRightColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
              AI Naming... {enrichment.percent}%
            </div>
          ) : enrichment.status === 'AI_ENRICHED' ? (
            <div style={{ fontSize: 13, color: 'var(--green)', fontWeight: 500 }}>
              ✓ AI Enriched
            </div>
          ) : (
            <button onClick={handleEnrich} style={{ background: 'var(--accent)', color: 'white', border: 'none', padding: '6px 12px', borderRadius: 6, fontSize: 13, cursor: 'pointer', fontWeight: 500 }}>
              Enhance Cluster Names with AI
            </button>
          )}
          <ExportMenu />
        </div>
      </div>

      <SectionHeader title="3R INTELLIGENCE SUMMARY" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 32 }}>
        <StatCard label="Total Tickets" value={data.total_tickets}                        icon={Ticket}       color="var(--accent)"  bg="var(--accent-bg)"  />
        <StatCard label="RUNNER"        value={data.runner_count}    sub={`${data.runner_percentage}% of total`}     icon={AlertTriangle}color="var(--red)"     bg="var(--red-bg)"    onClick={() => navigate('/tickets?three_r_category=RUNNER')} />
        <StatCard label="REPEATER"      value={data.repeater_count}  sub={`${data.repeater_percentage}% of total`}   icon={TrendingUp}   color="var(--amber)"   bg="var(--amber-bg)"  onClick={() => navigate('/tickets?three_r_category=REPEATER')} />
        <StatCard label="RARE"          value={data.rare_count}      sub={`${data.rare_percentage}% of total`}       icon={Layers}       color="var(--purple)"  bg="var(--purple-bg)" onClick={() => navigate('/tickets?three_r_category=RARE')} />
      </div>

      <SectionHeader title="PATTERN INSIGHTS" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 32 }}>
        <InsightCard 
          title="Most Active Pattern" 
          value={mostActive ? mostActive.cluster_name : 'None'} 
          sub={mostActive ? `${mostActive.ticket_count} incidents` : ''} 
          icon={Activity} 
        />
        <InsightCard 
          title="Highest Impact Pattern" 
          value={highestImpact ? highestImpact.cluster_name : 'None'} 
          sub={highestImpact ? `Classified as ${highestImpact.three_r_category}` : ''} 
          icon={AlertTriangle} 
        />
        <InsightCard 
          title="Top Affected CI" 
          value={topCI ? topCI[0] : 'None'} 
          sub={topCI ? `${topCI[1]} clustered incidents` : ''} 
          icon={Cpu} 
        />
        <InsightCard 
          title="Top Assignment Group" 
          value={topGroup ? topGroup[0] : 'None'} 
          sub={topGroup ? `${topGroup[1]} clustered incidents` : ''} 
          icon={Users} 
        />
      </div>

      <SectionHeader title="TREND / DISTRIBUTION" />
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 20, marginBottom: 32 }}>
        <Card>
          <div style={{ fontWeight: 600, marginBottom: 18, fontSize: 14 }}>Top 10 Recurring Patterns</div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={barData} layout="vertical" margin={{ left: 8, right: 16 }}>
              <XAxis type="number" stroke="transparent" tick={TICK} />
              <YAxis type="category" dataKey="name" width={170} stroke="transparent" tick={TICK} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: 'rgba(15,98,254,0.06)' }} formatter={(val) => [val, 'Tickets']} />
              <Bar dataKey="tickets" radius={[0, 6, 6, 0]}
                fill="url(#blueGrad)"
                onClick={(data) => navigate(`/clusters?cluster_id=${data.id}`)}
                style={{ cursor: 'pointer' }}
              />
              <defs>
                <linearGradient id="blueGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%"   stopColor="var(--accent)"  />
                  <stop offset="100%" stopColor="var(--purple)" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <div style={{ fontWeight: 600, marginBottom: 18, fontSize: 14 }}>3R Distribution</div>
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <defs>
                <linearGradient id="pieBlue" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%"   stopColor="var(--accent)" />
                  <stop offset="100%" stopColor="var(--purple)" />
                </linearGradient>
              </defs>
              <Pie data={pieData} cx="50%" cy="45%" innerRadius={72} outerRadius={110}
                dataKey="value" paddingAngle={3}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={{ stroke: 'var(--border2)' }}>
                <Cell fill="var(--red)" />
                <Cell fill="var(--amber)" />
                <Cell fill="var(--purple)" />
              </Pie>
              <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(val) => [val, 'Tickets']} />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div style={{ fontWeight: 600, fontSize: 14 }}>Pattern Details</div>
          <button className="btn-ghost" style={{ fontSize: 12, padding: '4px 10px' }} onClick={() => navigate('/clusters')}>View All Clusters</button>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 800 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                {['#', 'Cluster Name', 'Category', 'Tickets', 'Top CI', 'Top Group', 'Sample Issues'].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '8px 14px', color: 'var(--text2)', fontWeight: 500, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.top_clusters.map((c, i) => (
                <tr 
                  key={c.cluster_id} 
                  className="data-row" 
                  style={{ borderBottom: '1px solid var(--border)', cursor: 'pointer' }}
                  onClick={() => navigate(`/clusters?cluster_id=${c.cluster_id}`)}
                >
                  <td style={{ padding: '11px 14px', color: 'var(--text2)', fontSize: 12 }}>{i + 1}</td>
                  <td style={{ padding: '11px 14px', fontWeight: 600, fontSize: 13 }}>{c.cluster_name}</td>
                  <td style={{ padding: '11px 14px' }}>
                    <Badge color={c.three_r_category === 'RUNNER' ? 'var(--red)' : c.three_r_category === 'REPEATER' ? 'var(--amber)' : c.three_r_category === 'RARE' ? 'var(--purple)' : 'var(--text2)'}>
                      {c.three_r_category || 'UNCLASSIFIED'}
                    </Badge>
                  </td>
                  <td style={{ padding: '11px 14px' }}>
                    <span style={{ background: 'var(--accent-bg)', color: 'var(--accent-h)', padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600 }}>
                      {c.ticket_count}
                    </span>
                  </td>
                  <td style={{ padding: '11px 14px', color: 'var(--text)', fontSize: 12 }}>
                    {c.top_ci || '-'}
                  </td>
                  <td style={{ padding: '11px 14px', color: 'var(--text)', fontSize: 12 }}>
                    {c.top_group || '-'}
                  </td>
                  <td style={{ padding: '11px 14px', color: 'var(--text2)', fontSize: 12, maxWidth: 300, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {c.sample_tickets.slice(0, 2).map(t => t.short_description).join(' · ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Flagged problem clusters */}
      {flaggedClusters.length > 0 && (
        <Card style={{ marginTop: 20, border: '1.5px solid var(--red)', borderRadius: 'var(--radius)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--red)', display: 'inline-block', flexShrink: 0 }} />
            <span style={{ fontWeight: 600, fontSize: 14, color: 'var(--red)' }}>
              Problem Clusters ({flaggedClusters.length})
            </span>
            <span style={{ fontSize: 12, color: 'var(--text2)', marginLeft: 4 }}>
              — flagged from Clusters page
            </span>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                {['#', 'Cluster Name', 'Tickets'].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '8px 14px', color: 'var(--text2)', fontWeight: 500, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {flaggedClusters.map((c, i) => (
                <tr 
                  key={c.id} 
                  className="data-row" 
                  style={{ borderBottom: '1px solid var(--border)', cursor: 'pointer' }}
                  onClick={() => navigate(`/clusters?cluster_id=${c.id}`)}
                >
                  <td style={{ padding: '11px 14px', color: 'var(--text2)', fontSize: 12, width: 40 }}>{i + 1}</td>
                  <td style={{ padding: '11px 14px', fontWeight: 600, fontSize: 13 }}>{c.name}</td>
                  <td style={{ padding: '11px 14px', fontSize: 12 }}>{c.tickets}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}

function SectionHeader({ title }) {
  return (
    <div style={{ 
      fontSize: 12, 
      fontWeight: 700, 
      color: 'var(--text2)', 
      textTransform: 'uppercase', 
      letterSpacing: '0.1em', 
      marginBottom: 16,
      borderBottom: '1px solid var(--border)',
      paddingBottom: 8
    }}>
      {title}
    </div>
  )
}

function InsightCard({ title, value, sub, icon: Icon }) {
  return (
    <Card style={{ padding: '16px 20px', display: 'flex', alignItems: 'flex-start', gap: 16 }}>
      <div style={{ background: 'var(--surface2)', padding: 10, borderRadius: 'var(--radius)', color: 'var(--accent)' }}>
        <Icon size={20} />
      </div>
      <div>
        <div style={{ fontSize: 12, color: 'var(--text2)', fontWeight: 500, marginBottom: 4 }}>{title}</div>
        <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 180 }}>{value}</div>
        {sub && <div style={{ fontSize: 11, color: 'var(--text2)', marginTop: 4 }}>{sub}</div>}
      </div>
    </Card>
  )
}

function Loader() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16 }}>
      {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton" style={{ height: 100, borderRadius: 'var(--radius)' }} />)}
    </div>
  )
}

function Empty({ msg }) {
  return (
    <div style={{ textAlign: 'center', padding: '80px 20px', color: 'var(--text2)' }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>📈</div>
      <div style={{ fontSize: 15, fontWeight: 500, color: 'var(--text)', marginBottom: 8 }}>Dashboard Unavailable</div>
      <div style={{ fontSize: 13 }}>{msg}</div>
    </div>
  )
}
