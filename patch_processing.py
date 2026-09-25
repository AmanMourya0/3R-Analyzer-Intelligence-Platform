import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

new_screen = """function ProcessingScreen() {
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
}"""

start_idx = content.find("function ProcessingScreen")
end_idx = content.find("// ── Toast ─────────────────────────────────────────────────────────────────────")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_screen + "\n\n" + content[end_idx:]
    with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched ProcessingScreen in App.jsx.")
else:
    print("Could not find boundaries in App.jsx")
