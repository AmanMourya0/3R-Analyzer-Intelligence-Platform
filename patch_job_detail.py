import re

with open('frontend/src/pages/Jobs.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace JobDetailPanel
new_panel = """function JobDetailPanel({ jobId, onClose, onViewResults }) {
   const [job, setJob] = useState(null)
   const [loading, setLoading] = useState(true)
   const [error, setError] = useState('')

   useEffect(() => {
      let active = true
      setLoading(true)
      setError('')
      getJob(jobId).then(res => {
         if (active) {
            setJob(res.data)
            setLoading(false)
         }
      }).catch(err => {
         if (active) {
            console.error(err)
            setError('Unable to load job details.\\nThe job may no longer exist or the server may be unavailable.')
            setLoading(false)
         }
      })
      return () => { active = false }
   }, [jobId])

   useEffect(() => {
      const originalOverflowX = document.body.style.overflowX
      document.body.style.overflowX = 'hidden'
      return () => {
         document.body.style.overflowX = originalOverflowX
      }
   }, [])

   const handleBackdropClick = (e) => {
      if (e.target === e.currentTarget) {
         onClose();
      }
   };

   const overlayStyle = {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      zIndex: 1000,
      display: 'flex',
      justifyContent: 'flex-end',
      backdropFilter: 'blur(2px)'
   };

   const drawerStyle = {
      width: 500,
      maxWidth: '100%',
      backgroundColor: 'var(--bg)',
      borderLeft: '1px solid var(--border)',
      height: '100%',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      boxShadow: '-4px 0 24px rgba(0,0,0,0.5)'
   };

   if (loading) {
      return (
         <div onClick={handleBackdropClick} style={overlayStyle}>
            <div style={drawerStyle} className="fade-up">
               <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, background: 'var(--bg)', zIndex: 10 }}>
                  <h3 style={{ fontSize: 16, fontWeight: 600, margin: 0 }}>Job Details</h3>
                  <button onClick={onClose} className="btn-ghost" style={{ padding: 8, borderColor: 'transparent' }}><X size={20} /></button>
               </div>
               <div style={{ padding: 24 }}>
                  <Loader />
               </div>
            </div>
         </div>
      )
   }

   if (error) {
      return (
         <div onClick={handleBackdropClick} style={overlayStyle}>
            <div style={drawerStyle} className="fade-up">
               <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, background: 'var(--bg)', zIndex: 10 }}>
                  <h3 style={{ fontSize: 16, fontWeight: 600, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                     <Activity size={18} color="var(--accent)" />
                     Job Details
                  </h3>
                  <button onClick={onClose} className="btn-ghost" style={{ padding: 8, borderColor: 'transparent' }}><X size={20} /></button>
               </div>
               <div style={{ padding: 30, textAlign: 'center', color: 'var(--text2)' }}>
                  <AlertCircle size={32} style={{ marginBottom: 12, color: 'var(--red)' }} />
                  <div style={{ fontSize: 13, whiteSpace: 'pre-wrap' }}>{error}</div>
               </div>
            </div>
         </div>
      )
   }

   if (!job) return null

   const invariantFailed = job.status === 'COMPLETED' && (
       (job.total_runners || 0) + (job.total_repeaters || 0) + (job.total_rares || 0) !== (job.total_incidents || 0)
   )

   return (
      <div onClick={handleBackdropClick} style={overlayStyle}>
         <div style={drawerStyle} className="fade-up">
            <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, background: 'var(--bg)', zIndex: 10 }}>
               <div>
                  <div style={{ fontSize: 13, color: 'var(--text2)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Job Detail</div>
                  <h3 style={{ fontSize: 20, fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
                     <Activity size={20} color="var(--accent)" />
                     {job.id ? job.id.split('-')[0] : '—'}
                  </h3>
               </div>
               <button onClick={onClose} className="btn-ghost" style={{ padding: 8, borderColor: 'transparent' }}><X size={20} /></button>
            </div>

            <div style={{ padding: 24 }}>
               <div style={{ marginBottom: 24 }}>
                  <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>Full Job ID</div>
                  <div style={{ fontSize: 13, fontFamily: 'monospace', color: 'var(--text)' }}>{job.id || '—'}</div>
               </div>

               <div style={{ marginBottom: 24 }}>
                  <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>Dataset Source</div>
                  <div style={{ fontSize: 13, color: 'var(--text)', wordBreak: 'break-all' }}>{job.dataset_path || '—'}</div>
               </div>

               <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
                  <div style={{ flex: 1 }}>
                     <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>Status</div>
                     <StatusBadge status={job.status} />
                  </div>
                  <div style={{ flex: 1 }}>
                     <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>Duration</div>
                     <div style={{ fontSize: 13, color: 'var(--text)' }}>{job.processing_time_seconds != null ? `${Number(job.processing_time_seconds).toFixed(1)}s` : '—'}</div>
                  </div>
               </div>

               <div style={{ marginBottom: 32, padding: 16, background: 'var(--surface2)', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 12 }}>Progress</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                     <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text)' }}>{job.progress_stage || 'Unknown'}</span>
                     <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--accent)' }}>{job.progress_percent ?? 0}%</span>
                  </div>
                  <div style={{ height: 6, background: 'var(--border)', borderRadius: 3, overflow: 'hidden' }}>
                     <div style={{ height: '100%', width: `${job.progress_percent ?? 0}%`, background: 'var(--accent)', transition: 'width 0.3s' }} />
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text2)', marginTop: 10 }}>{job.progress_message || ''}</div>
                  {job.error_message && (
                     <div style={{ marginTop: 10, padding: 10, background: 'rgba(244,63,94,0.1)', color: 'var(--red)', fontSize: 12, borderRadius: 6 }}>
                        {job.error_message}
                     </div>
                  )}
               </div>

               {job.status === 'COMPLETED' && (
                  <div style={{ marginBottom: 32 }}>
                     <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>Analysis Results</div>
                     <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                        <ResultMetric label="Total Tickets" value={job.total_incidents} />
                        <ResultMetric label="Clusters" value={job.total_clusters} />
                        <ResultMetric label="Runners" value={job.total_runners} color="var(--red)" />
                        <ResultMetric label="Repeaters" value={job.total_repeaters} color="var(--amber)" />
                        <ResultMetric label="Rares" value={job.total_rares} color="var(--purple)" />
                     </div>

                     {invariantFailed && (
                        <div style={{ marginTop: 16, padding: 12, background: 'rgba(244,63,94,0.1)', border: '1px solid var(--red)', borderRadius: 8, display: 'flex', gap: 8 }}>
                           <AlertTriangle size={16} color="var(--red)" style={{ flexShrink: 0, marginTop: 2 }} />
                           <div style={{ fontSize: 12, color: 'var(--red)', lineHeight: 1.4 }}>
                              <strong>Data Integrity Warning:</strong>
                              <br />
                              The sum of 3R categories does not equal total tickets processed. This dataset may contain unclassified or corrupted records.
                           </div>
                        </div>
                     )}
                  </div>
               )}

               <div style={{ padding: 16, background: 'var(--surface2)', borderRadius: 8, border: '1px dashed var(--border)', marginBottom: 24 }}>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                     <Info size={16} color="var(--accent)" style={{ flexShrink: 0, marginTop: 2 }} />
                     <div style={{ fontSize: 12, color: 'var(--text2)', lineHeight: 1.5 }}>
                        Viewing results navigates to the global dashboards. The current system architecture aggregates all analysis into a single global state and does not isolate results by job.
                     </div>
                  </div>
               </div>

               <button 
                  className="btn-primary" 
                  style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, padding: '12px' }}
                  onClick={onViewResults}
                  disabled={job.status !== 'COMPLETED'}
               >
                  View Active Dashboards <ExternalLink size={16} />
               </button>
            </div>
         </div>
      </div>
   )
}"""

start_idx = content.find("function JobDetailPanel")
end_idx = content.find("function ResultMetric")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_panel + "\n\n" + content[end_idx:]
    with open('frontend/src/pages/Jobs.jsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched JobDetailPanel.")
else:
    print("Could not find JobDetailPanel boundaries.")
