import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Clusters from './pages/Clusters'
import CIAnalysis from './pages/CIAnalysis'
import Tickets from './pages/Tickets'
import AssignedGroup from './pages/AssignedGroup'
import Home from './pages/Home'
import Demo from './pages/Demo'
import Jobs from './pages/Jobs'
import { uploadCSV, getHealth, warmup, loadSample, getStatus } from './api'
import { CheckCircle, AlertCircle, Info, X, Loader as SpinIcon } from 'lucide-react'
import { applyTheme, getSavedTheme } from './theme'

// ── Processing steps overlay ──────────────────────────────────────────────────
const STEPS = [
  { id: 'LOADING_DATA', label: 'Loading Data' },
  { id: 'APPLYING_SCOPE', label: 'Applying Scope' },
  { id: 'PREPROCESSING', label: 'Data Preprocessing' },
  { id: 'GENERATING_EMBEDDINGS', label: 'Generating Embeddings' },
  { id: 'STORING_EMBEDDINGS', label: 'Storing Embeddings' },
  { id: 'CLUSTERING', label: 'Semantic Clustering' },
  { id: 'CLUSTER_ANALYSIS', label: 'Cluster Analysis' },
  { id: 'NAMING_CLUSTERS', label: 'Naming Clusters' },
  { id: 'RECURRENCE_ANALYSIS', label: 'Recurrence Analysis' },
  { id: 'THREE_R_CLASSIFICATION', label: '3R Classification' },
  { id: 'PERSISTING_RESULTS', label: 'Saving Results' },
]

function ProcessingScreen() {
  const [jobState, setJobState] = useState({ stage: 'PENDING', message: 'Initializing...', percent: 0, status: 'processing' })

  useEffect(() => {
    let active = true
    const poll = async () => {
      try {
        const s = await getStatus()
        if (!active) return
        const { status, message, stage, percent } = s.data
        if (status === 'processing' || status === 'done' || status === 'error') {
           setJobState(prev => {
               // Protect against backwards regression in progress
               const newIdx = STEPS.findIndex(x => x.id === stage)
               const oldIdx = STEPS.findIndex(x => x.id === prev.stage)
               if (newIdx !== -1 && oldIdx !== -1 && newIdx < oldIdx && status === 'processing') {
                   return prev // ignore stale out-of-order packet
               }
               return { status, message, stage, percent }
           })
        }
        if (status === 'done' || status === 'error') {
            clearInterval(iv)
        }
      } catch { /* ignore */ }
    }
    
    poll()
    const iv = setInterval(poll, 2000)
    return () => { active = false; clearInterval(iv) }
  }, [])

  const currentIdx = STEPS.findIndex(s => s.id === jobState.stage)
  const safeIdx = currentIdx >= 0 ? currentIdx : (jobState.status === 'done' ? STEPS.length : 0)

  return (
    <div style={{
      height: '100vh', width: '100vw', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg)', padding: 20, overflow: 'hidden'
    }}>
      <div className="fade-up" style={{
        background: 'var(--surface)', borderRadius: 12, padding: '24px 32px',
        width: 440, maxWidth: '100%', boxShadow: 'var(--shadow)', border: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column', maxHeight: 'calc(100vh - 40px)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>
            {jobState.status === 'error' ? '❌' : jobState.status === 'done' ? '✅' : '⚙️'}
          </div>
          <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--text)', marginBottom: 4 }}>
            {jobState.status === 'error' ? 'Processing Failed' : jobState.status === 'done' ? 'Processing Completed' : 'Processing Tickets…'}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text2)', minHeight: 18 }}>
            {jobState.message || 'AI is analysing your data.'}
          </div>
        </div>

        {jobState.status !== 'error' && (
           <div style={{ marginBottom: 20 }}>
             <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 6, fontWeight: 600 }}>
                <span style={{ color: 'var(--text2)' }}>Progress</span>
                <span style={{ color: 'var(--accent)' }}>{jobState.percent || 0}%</span>
             </div>
             <div style={{ width: '100%', height: 4, background: 'var(--surface2)', borderRadius: 2, overflow: 'hidden' }}>
                <div style={{ 
                   height: '100%', background: 'var(--accent)', 
                   width: `${jobState.percent || 0}%`, transition: 'width 0.5s ease-out' 
                }} />
             </div>
           </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, overflowY: 'auto' }}>
          {STEPS.map((s, i) => {
            const done   = jobState.status === 'done' || (safeIdx > i)
            const active = jobState.status === 'processing' && safeIdx === i
            return (
              <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 10, opacity: (done || active) ? 1 : 0.4 }}>
                <div style={{
                  width: 20, height: 20, borderRadius: '50%', flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: done ? 'var(--green-bg)' : active ? 'var(--accent-bg)' : 'transparent',
                  border: `1.5px solid ${done ? 'var(--green)' : active ? 'var(--accent)' : 'var(--border)'}`,
                  transition: 'all 0.4s',
                }}>
                  {done
                    ? <CheckCircle size={10} color="var(--green)" />
                    : active
                      ? <SpinIcon size={10} color="var(--accent)" style={{ animation: 'spin 1s linear infinite' }} />
                      : <span style={{ fontSize: 8, color: 'var(--text3)', fontWeight: 600 }}>{i + 1}</span>
                  }
                </div>
                <span style={{
                  fontSize: 12, fontWeight: active ? 600 : done ? 500 : 400,
                  color: done ? 'var(--green)' : active ? 'var(--text)' : 'var(--text3)',
                  transition: 'color 0.3s',
                }}>
                  {s.label}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function Toast({ toast, onClose }) {
  if (!toast) return null
  const cfg = {
    success: { icon: CheckCircle, color: 'var(--green)',  border: 'rgba(34,197,94,0.3)'  },
    error:   { icon: AlertCircle, color: 'var(--red)',    border: 'rgba(244,63,94,0.3)'  },
    info:    { icon: Info,        color: 'var(--accent)', border: 'rgba(15,98,254,0.3)' },
  }[toast.type] || { icon: Info, color: 'var(--accent)', border: 'var(--border)' }
  const Icon = cfg.icon
  return (
    <div className="fade-up" style={{
      position: 'fixed', bottom: 28, right: 28, zIndex: 999,
      background: 'var(--surface)', border: `1px solid ${cfg.border}`,
      borderRadius: 12, padding: '14px 18px',
      display: 'flex', alignItems: 'center', gap: 12,
      boxShadow: '0 8px 32px rgba(0,0,0,0.4)', maxWidth: 360,
    }}>
      <Icon size={18} color={cfg.color} style={{ flexShrink: 0 }} />
      <span style={{ fontSize: 13, color: 'var(--text)', flex: 1 }}>{toast.msg}</span>
      <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text2)', cursor: 'pointer', padding: 2 }}>
        <X size={14} />
      </button>
    </div>
  )
}

// ── Page header (used inside sidebar layout) ──────────────────────────────────
function PageHeader({ theme, setTheme }) {
  const loc = useLocation()
  const titles = {
    '/dashboard': 'Dashboard',
    '/clusters':  'Ticket Clusters',
    '/ci':        'CI Analysis',
    '/groups':    'Assigned Group Analysis',
    '/tickets':   'All Tickets',
    '/demo':      'Demo Mode',
    '/jobs':      'Job History',
  }
  const isDark = theme === 'dark'

  return (
    <div style={{
      height: 56, borderBottom: '1px solid var(--border)',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 32px', background: 'var(--surface)', flexShrink: 0,
    }}>
      <span style={{ fontWeight: 600, fontSize: 15, color: 'var(--text)' }}>
        {titles[loc.pathname] || '3R Analyzer'}
      </span>
      <button onClick={() => { const n = isDark ? 'light' : 'dark'; applyTheme(n); setTheme(n) }}
        title={isDark ? 'Switch to Light' : 'Switch to Dark'}
        style={{ width: 36, height: 36, borderRadius: 10, border: '1px solid var(--border)', background: 'var(--surface2)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 17 }}>
        {isDark ? '☀️' : '🌙'}
      </button>
    </div>
  )
}

// ── Main layout router ────────────────────────────────────────────────────────
function AppInner({ onUpload, onSampleLoad, processing, toast, closeToast, dataLoaded, serverReady, theme, setTheme, refreshKey }) {
  const navigate = useNavigate()
  const loc = useLocation()
  const isHome = loc.pathname === '/home' || loc.pathname === '/'

  useEffect(() => {
    if (refreshKey > 0) navigate('/dashboard')
  }, [refreshKey])

  // Full-screen processing — no sidebar
  if (processing) {
    return (
      <>
        <ProcessingScreen />
        <Toast toast={toast} onClose={closeToast} />
      </>
    )
  }

  // Home page — no sidebar, full screen
  if (isHome) {
    return (
      <>
        <Routes>
          <Route path="/home" element={<Home onUpload={onUpload} processing={processing} theme={theme} setTheme={setTheme} />} />
          <Route path="/"     element={<Navigate to="/home" replace />} />
          <Route path="*"     element={<Navigate to="/home" replace />} />
        </Routes>
        <Toast toast={toast} onClose={closeToast} />
      </>
    )
  }

  // App pages — with sidebar
  return (
    <div style={{ display: 'flex', height: '100%' }}>
      <Sidebar onUpload={onUpload} onSampleLoad={onSampleLoad} processing={processing} theme={theme} />
      <div style={{ marginLeft: 200, flex: 1, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <PageHeader theme={theme} setTheme={setTheme} />
        <main style={{ flex: 1, padding: '20px 24px', overflowY: 'auto' }}>
          <Routes>
            <Route path="/dashboard" element={<Dashboard key={refreshKey} />} />
            <Route path="/clusters"  element={<Clusters />} />
            <Route path="/ci"        element={<CIAnalysis />} />
            <Route path="/groups"    element={<AssignedGroup />} />
            <Route path="/tickets"   element={<Tickets />} />
            <Route path="/jobs"      element={<Jobs />} />
            <Route path="/demo"      element={<Demo onUpload={onUpload} onSampleLoad={onSampleLoad} processing={processing} dataLoaded={dataLoaded} refreshKey={refreshKey} />} />
            <Route path="*"          element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
      <Toast toast={toast} onClose={closeToast} />
    </div>
  )
}

// ── Root App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [processing, setProcessing] = useState(false)
  const [toast, setToast]           = useState(null)
  const [dataLoaded, setDataLoaded] = useState(false)
  const [serverReady, setServerReady] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)
  const [theme, setTheme] = useState(() => {
    const saved = getSavedTheme(); applyTheme(saved); return saved
  })

  useEffect(() => {
    let attempts = 0
    function ping() {
      getHealth()
        .then(r => {
          setServerReady(true)
          setDataLoaded(r.data.data_loaded)
          warmup().catch(() => {})
        })
        .catch(() => { if (++attempts < 20) setTimeout(ping, 3000) })
    }
    ping()
  }, [])

  function showToast(type, msg) {
    setToast({ type, msg })
    setTimeout(() => setToast(null), 5000)
  }

  async function handleUpload(file) {
    setProcessing(true)
    try {
      await uploadCSV(file)
      pollStatus()
    } catch (e) {
      setProcessing(false)
      showToast('error', e.response?.data?.detail || 'Upload failed.')
    }
  }

  async function handleLoadSample() {
    setProcessing(true)
    try {
      await loadSample()
      pollStatus()
    } catch (e) {
      setProcessing(false)
      showToast('error', e.response?.data?.detail || 'Failed to load sample data.')
    }
  }

  function pollStatus() {
    const iv = setInterval(async () => {
      try {
        const s = await getStatus()
        const { status, message, result } = s.data
        if (status === 'processing') showToast('info', message || 'Processing...')
        else if (status === 'done') {
          clearInterval(iv)
          setProcessing(false)
          setDataLoaded(true)
          setRefreshKey(k => k + 1)
          showToast('success', `${result.total_tickets} tickets → ${result.total_clusters} clusters`)
        } else if (status === 'error') {
          clearInterval(iv)
          setProcessing(false)
          showToast('error', message || 'Processing failed.')
        }
      } catch { /* ignore */ }
    }, 3000)
  }

  return (
    <BrowserRouter>
      <AppInner
        onUpload={handleUpload}
        onSampleLoad={handleLoadSample}
        processing={processing}
        toast={toast}
        closeToast={() => setToast(null)}
        dataLoaded={dataLoaded}
        serverReady={serverReady}
        theme={theme}
        setTheme={setTheme}
        refreshKey={refreshKey}
      />
    </BrowserRouter>
  )
}
