import React, { useEffect, useState, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { getJobs, getJob } from '../api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import { ChevronLeft, ChevronRight, Clock, CheckCircle, AlertCircle, PlayCircle, Loader as SpinIcon, Activity, ExternalLink, Info, AlertTriangle, X } from 'lucide-react'

export default function Jobs() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  
  const initialPage = parseInt(searchParams.get('page') || '1', 10)
  const jobId = searchParams.get('job_id')
  
  const [jobs, setJobs] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(initialPage)
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const pageSize = 20
  
  const activeJobsExist = jobs.some(j => ['QUEUED', 'RUNNING', 'PROCESSING'].includes(j.status))

  const loadData = async (currentPage) => {
    try {
      const res = await getJobs({ page: currentPage, page_size: pageSize })
      setJobs(res.data.jobs || [])
      setTotal(res.data.total || 0)
      setTotalPages(res.data.total_pages || 1)
    } catch (e) {
      console.error(e)
      setError('Failed to load jobs history.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    setLoading(true)
    loadData(page)
  }, [page])
  
  useEffect(() => {
    let iv
    if (activeJobsExist) {
       iv = setInterval(() => {
          loadData(page)
       }, 3000)
    }
    return () => clearInterval(iv)
  }, [activeJobsExist, page])

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage)
      setSearchParams({ page: newPage, ...(jobId ? { job_id: jobId } : {}) }, { replace: true })
    }
  }
  
  const handleSelect = (id) => {
     setSearchParams({ page, job_id: id }, { replace: true })
  }
  
  const handleCloseDetail = () => {
     setSearchParams({ page }, { replace: true })
  }

  return (
    <div className="fade-up" style={{ paddingBottom: 60, display: 'flex', gap: 20 }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text)' }}>Job Operations</h1>
          <p style={{ fontSize: 13, color: 'var(--text2)', marginTop: 4 }}>Monitor dataset processing and AI analysis history.</p>
        </div>

        {error ? (
          <Empty msg={error} />
        ) : loading ? (
          <Loader />
        ) : jobs.length === 0 ? (
          <Empty msg="No jobs found. Import a dataset to start." />
        ) : (
          <Card style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontSize: 13, color: 'var(--text2)', fontWeight: 500 }}>
                Showing {((page - 1) * pageSize) + 1} - {Math.min(page * pageSize, total)} of {total.toLocaleString()} jobs
              </div>
              
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <button 
                  onClick={() => handlePageChange(page - 1)} 
                  disabled={page === 1}
                  className="btn-ghost"
                  style={{ padding: 6 }}
                >
                  <ChevronLeft size={16} />
                </button>
                <span style={{ fontSize: 13, fontWeight: 500 }}>Page {page} of {totalPages}</span>
                <button 
                  onClick={() => handlePageChange(page + 1)} 
                  disabled={page === totalPages}
                  className="btn-ghost"
                  style={{ padding: 6 }}
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
            
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)', background: 'var(--surface)' }}>
                    {['Status', 'Dataset', 'Progress', 'Duration', 'Tickets', 'Clusters', 'Date'].map(h => (
                      <th key={h} style={{ textAlign: 'left', padding: '10px 12px', color: 'var(--text2)', fontWeight: 500, fontSize: 11, whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {jobs.map(j => (
                    <tr 
                      key={j.id} 
                      className="data-row" 
                      style={{ 
                         borderBottom: '1px solid var(--border)', 
                         cursor: 'pointer',
                         background: jobId === j.id ? 'var(--surface2)' : 'transparent'
                      }}
                      onClick={() => handleSelect(j.id)}
                    >
                      <td style={td}>
                         <StatusBadge status={j.status} />
                      </td>
                      <td style={{ ...td, maxWidth: 200, fontWeight: 500 }}>
                        <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                           {formatDatasetPath(j.dataset_path)}
                        </div>
                      </td>
                      <td style={{ ...td, maxWidth: 150 }}>
                         <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontSize: 11 }}>
                           {j.progress_percent ?? 0}% - {j.progress_stage || 'Unknown'}
                         </div>
                      </td>
                      <td style={td}>{j.processing_time_seconds ? `${Math.round(j.processing_time_seconds)}s` : '—'}</td>
                      <td style={td}>{j.total_incidents?.toLocaleString() || '—'}</td>
                      <td style={td}>{j.total_clusters?.toLocaleString() || '—'}</td>
                      <td style={{ ...td, color: 'var(--text2)', whiteSpace: 'nowrap' }}>{j.created_at ? new Date(j.created_at).toLocaleString() : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>

      {jobId && (
        <JobDetailPanel 
           jobId={jobId} 
           onClose={handleCloseDetail} 
           onViewResults={() => navigate('/dashboard')}
        />
      )}
    </div>
  )
}

function JobDetailPanel({ jobId, onClose, onViewResults }) {
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
            setError('Unable to load job details.\nThe job may no longer exist or the server may be unavailable.')
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
}

function ResultMetric({ label, value, color = 'var(--text)' }) {
   return (
      <div style={{ padding: 10, background: 'var(--surface2)', borderRadius: 8, border: '1px solid var(--border)' }}>
         <div style={{ fontSize: 11, color: 'var(--text2)', marginBottom: 2 }}>{label}</div>
         <div style={{ fontSize: 16, fontWeight: 700, color }}>{value != null ? Number(value).toLocaleString() : 0}</div>
      </div>
   )
}

function StatusBadge({ status }) {
   const colors = {
      'QUEUED': 'var(--text2)',
      'RUNNING': 'var(--accent)',
      'PROCESSING': 'var(--accent)',
      'COMPLETED': 'var(--green)',
      'FAILED': 'var(--red)'
   }
   
   return <Badge color={colors[status] || 'var(--text2)'}>{status || 'UNKNOWN'}</Badge>
}

function formatDatasetPath(path) {
   if (!path) return '—'
   const parts = String(path).split(/[/\\]/)
   return parts[parts.length - 1]
}

const td = { padding: '10px 12px', fontSize: 12 }

function Loader() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height: 44, borderRadius: i === 0 ? '12px 12px 0 0' : i === 7 ? '0 0 12px 12px' : 0 }} />
      ))}
    </div>
  )
}

function Empty({ msg }) {
  return (
    <div style={{ textAlign: 'center', padding: '80px 20px', color: 'var(--text2)' }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>⏱️</div>
      <div style={{ fontSize: 15, fontWeight: 500, color: 'var(--text)', marginBottom: 8 }}>No Processing History</div>
      <div style={{ fontSize: 13 }}>{msg}</div>
    </div>
  )
}
