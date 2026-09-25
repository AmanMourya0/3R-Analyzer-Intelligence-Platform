import { useEffect, useState } from 'react'
import { Upload, CheckCircle, Circle, Loader as SpinIcon } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts'
import { getDashboard, getStatus } from '../api'
import Card from '../components/Card'
import StatCard from '../components/StatCard'
import { Ticket, Layers, TrendingUp, AlertTriangle } from 'lucide-react'

const TOOLTIP_STYLE = {
  background: 'var(--surface)', border: '1px solid var(--border)',
  color: 'var(--text)', borderRadius: 8, fontSize: 12,
}
const TICK = { fill: 'var(--text2)', fontSize: 11 }

const STEPS = [
  'CSV Uploaded',
  'Data Validated',
  'Data Preprocessing',
  'Embedding & Clustering',
  'Cluster Naming',
  'Enrichment',
]

function msgToStep(msg = '') {
  const m = msg.toLowerCase()
  if (m.includes('validat') || m.includes('read'))     return 1
  if (m.includes('preprocess') || m.includes('clean')) return 2
  if (m.includes('embed') || m.includes('cluster'))    return 3
  if (m.includes('nam'))                               return 4
  if (m.includes('enrich') || m.includes('saving'))    return 5
  return 1
}

export default function Demo({ onUpload, processing, dataLoaded, refreshKey }) {
  const [data, setData] = useState(null)
  const [stepIndex, setStepIndex] = useState(-1)
  const [dragOver, setDragOver] = useState(false)
  const [fileName, setFileName] = useState('')

  // When processing starts → immediately load cached results for right side
  useEffect(() => {
    if (processing && data === null) {
      getDashboard().then(r => setData(r.data)).catch(() => {})
    }
  }, [processing])

  // When new processing finishes → refresh right side
  useEffect(() => {
    if (refreshKey > 0) {
      getDashboard().then(r => setData(r.data)).catch(() => {})
      setStepIndex(STEPS.length)
    }
  }, [refreshKey])

  // Track processing steps
  useEffect(() => {
    if (!processing) return
    setStepIndex(0)
    const iv = setInterval(async () => {
      try {
        const s = await getStatus()
        const { status, message } = s.data
        if (status === 'processing') setStepIndex(msgToStep(message))
        if (status === 'done' || status === 'error') clearInterval(iv)
      } catch { /* ignore */ }
    }, 2000)
    return () => clearInterval(iv)
  }, [processing])

  function handleFile(file) {
    if (!file) return
    setFileName(file.name)
    setStepIndex(0)
    onUpload(file)
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file?.name.endsWith('.csv')) handleFile(file)
  }

  const barData = data ? data.top_clusters.map(c => ({ name: c.cluster_name, tickets: c.ticket_count })) : []
  const pieData = data ? [
    { name: 'Recurring', value: data.total_tickets - data.noise_ticket_count },
    { name: 'Unique',    value: data.noise_ticket_count },
  ] : []

  return (
    <div className="fade-up" style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 24, alignItems: 'start' }}>

      {/* LEFT — upload + steps */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div>
          <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text)', marginBottom: 4 }}>Demo Mode</h2>
          <p style={{ fontSize: 12, color: 'var(--text2)', lineHeight: 1.5 }}>
            Upload a CSV to process live. Pre-loaded results show on the right instantly.
          </p>
        </div>

        <label
          onDragOver={e => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            justifyContent: 'center', gap: 8, padding: '24px 16px',
            border: `2px dashed ${dragOver ? 'var(--accent)' : 'var(--border2)'}`,
            borderRadius: 12, cursor: processing ? 'not-allowed' : 'pointer',
            background: dragOver ? 'var(--accent-bg)' : 'var(--surface)',
            transition: 'all 0.15s', opacity: processing ? 0.55 : 1,
          }}
        >
          <Upload size={26} color="var(--accent)" />
          <span style={{ fontWeight: 600, fontSize: 13, color: 'var(--text)' }}>
            {fileName || 'Upload CSV'}
          </span>
          <span style={{ fontSize: 11, color: 'var(--text2)', textAlign: 'center' }}>
            {processing ? 'Processing…' : 'Click or drag & drop'}
          </span>
          <input type="file" accept=".csv" style={{ display: 'none' }} disabled={processing}
            onChange={e => handleFile(e.target.files[0])} />
        </label>

        {stepIndex >= 0 && (
          <Card style={{ padding: '16px 18px' }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text2)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Processing
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {STEPS.map((s, i) => {
                const done   = i < stepIndex || stepIndex >= STEPS.length
                const active = i === stepIndex && stepIndex < STEPS.length
                return (
                  <div key={s} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    {done
                      ? <CheckCircle size={15} color="var(--green)" />
                      : active
                        ? <SpinIcon size={15} color="var(--accent)" style={{ animation: 'spin 1s linear infinite' }} />
                        : <Circle size={15} color="var(--border2)" />
                    }
                    <span style={{
                      fontSize: 12,
                      color: done ? 'var(--green)' : active ? 'var(--text)' : 'var(--text3)',
                      fontWeight: active ? 600 : 400,
                    }}>{s}</span>
                  </div>
                )
              })}
            </div>
          </Card>
        )}

        {stepIndex >= STEPS.length && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8, padding: '12px 14px',
            background: 'var(--green-bg)', border: '1px solid rgba(34,197,94,0.3)', borderRadius: 10,
          }}>
            <CheckCircle size={15} color="var(--green)" />
            <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--green)' }}>
              Results updated →
            </span>
          </div>
        )}
      </div>

      {/* RIGHT — live results */}
      <div>
        {!data ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 400, gap: 12, color: 'var(--text3)' }}>
            <span style={{ fontSize: 48 }}>📊</span>
            <span style={{ fontSize: 13, color: 'var(--text2)' }}>Results appear here after upload</span>
          </div>
        ) : (
          <div className="fade-up">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 20 }}>
              <StatCard label="Total Tickets"    value={data.total_tickets}                    icon={Ticket}        color="var(--accent)"  bg="var(--accent-bg)"  />
              <StatCard label="Clusters Found"   value={data.total_clusters}                   icon={Layers}        color="var(--purple)"  bg="var(--purple-bg)"  />
              <StatCard label="Recurring"        value={`${data.recurring_issue_percentage}%`} icon={TrendingUp}    color="var(--green)"   bg="var(--green-bg)"   />
              <StatCard label="Unique Issues"    value={data.noise_ticket_count}               icon={AlertTriangle} color="var(--amber)"   bg="var(--amber-bg)"   />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 16, marginBottom: 16 }}>
              <Card>
                <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 12 }}>Top Recurring Clusters</div>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={barData} layout="vertical" margin={{ left: 8, right: 16 }}>
                    <XAxis type="number" stroke="transparent" tick={TICK} />
                    <YAxis type="category" dataKey="name" width={160} stroke="transparent" tick={TICK} />
                    <Tooltip contentStyle={TOOLTIP_STYLE} />
                    <Bar dataKey="tickets" radius={[0, 6, 6, 0]} fill="url(#dg)" />
                    <defs>
                      <linearGradient id="dg" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="var(--accent)" />
                        <stop offset="100%" stopColor="var(--purple)" />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </Card>
              <Card>
                <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 12 }}>Ticket Breakdown</div>
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85}
                      dataKey="value" paddingAngle={3}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      labelLine={{ stroke: 'var(--border2)' }}>
                      <Cell fill="var(--accent)" />
                      <Cell fill="var(--red)" />
                    </Pie>
                    <Tooltip contentStyle={TOOLTIP_STYLE} />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </div>

            <Card>
              <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 12 }}>Cluster Details</div>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)' }}>
                    {['#', 'Cluster Name', 'Tickets', 'Sample Issues'].map(h => (
                      <th key={h} style={{ textAlign: 'left', padding: '7px 12px', color: 'var(--text2)', fontWeight: 500, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.top_clusters.map((c, i) => (
                    <tr key={c.cluster_id} className="data-row" style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={td}>{i + 1}</td>
                      <td style={{ ...td, fontWeight: 600 }}>{c.cluster_name}</td>
                      <td style={td}>
                        <span style={{ background: 'var(--accent-bg)', color: 'var(--accent-h)', padding: '2px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600 }}>
                          {c.ticket_count}
                        </span>
                      </td>
                      <td style={{ ...td, color: 'var(--text2)' }}>{c.sample_tickets.slice(0, 2).join(' · ')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

const td = { padding: '9px 12px', fontSize: 12 }
