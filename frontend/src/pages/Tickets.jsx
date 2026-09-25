import { useEffect, useState, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getTickets, getClusters, getCIList, getGroupList } from '../api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import FilterBuilder from '../components/FilterBuilder'
import SortBuilder from '../components/SortBuilder'
import TicketDrawer from '../components/TicketDrawer'
import ExportMenu from '../components/ExportMenu'
import { ChevronLeft, ChevronRight } from 'lucide-react'

export default function Tickets() {
  const [searchParams, setSearchParams] = useSearchParams()
  
  // Parse state from URL
  const initialFilterStr = searchParams.get('filter') || ''
  let initialAst = null
  try { if (initialFilterStr) initialAst = JSON.parse(decodeURIComponent(initialFilterStr)) } catch(e) {}
  
  const initialSortStr = searchParams.get('sort') || ''
  let initialSorts = []
  try { if (initialSortStr) initialSorts = JSON.parse(decodeURIComponent(initialSortStr)) } catch(e) {}

  const initialPage = parseInt(searchParams.get('page') || '1', 10)
  
  // Also keep legacy params in sync if they exist
  const legacyCluster = searchParams.get('cluster_id')
  const legacyCategory = searchParams.get('three_r_category')

  const [tickets, setTickets] = useState([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  
  const [ciList, setCiList] = useState([])
  const [groupList, setGroupList] = useState([])
  
  // Active states
  const [ast, setAst] = useState(initialAst)
  const [sorts, setSorts] = useState(initialSorts)
  const [page, setPage] = useState(initialPage)
  const pageSize = 50

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedTicket, setSelectedTicket] = useState(null)

  useEffect(() => {
    Promise.all([getCIList(), getGroupList()])
      .then(([cir, gr]) => {
        setCiList(cir.data.ci_list || [])
        setGroupList(gr.data.group_list || [])
      })
      .catch(() => {})
  }, [])

  // Sync state to URL when filters change
  const syncToUrl = useCallback((newAst, newSorts, newPage) => {
    const newParams = new URLSearchParams(searchParams)
    
    if (newAst && newAst.conditions && newAst.conditions.length > 0) {
      newParams.set('filter', encodeURIComponent(JSON.stringify(newAst)))
    } else {
      newParams.delete('filter')
    }
    
    if (newSorts && newSorts.length > 0) {
      newParams.set('sort', encodeURIComponent(JSON.stringify(newSorts)))
    } else {
      newParams.delete('sort')
    }
    
    if (newPage > 1) {
      newParams.set('page', newPage)
    } else {
      newParams.delete('page')
    }
    
    setSearchParams(newParams, { replace: true })
  }, [searchParams, setSearchParams])

  const loadData = useCallback(() => {
    setLoading(true)
    const params = { page, page_size: pageSize }
    
    if (ast && ast.conditions && ast.conditions.length > 0) {
      params.filter = JSON.stringify(ast)
    }
    if (sorts && sorts.length > 0) {
      params.sort = JSON.stringify(sorts)
    }
    if (legacyCluster) params.cluster_id = legacyCluster
    if (legacyCategory) params.three_r_category = legacyCategory

    getTickets(params)
      .then(r => {
        setTickets(r.data.tickets || [])
        setTotal(r.data.total || 0)
        setTotalPages(r.data.total_pages || 1)
        setError('')
      })
      .catch((e) => {
        console.error(e)
        setError('Unable to execute this filter. Please review the conditions.')
      })
      .finally(() => setLoading(false))
  }, [ast, sorts, page, legacyCluster, legacyCategory])

  // Initial load or pagination/URL change
  useEffect(() => {
    loadData()
  }, [page, legacyCluster, legacyCategory])

  const handleRun = () => {
    setPage(1) // reset to page 1 on new filter
    syncToUrl(ast, sorts, 1)
    loadData()
  }

  const handleClear = () => {
    setAst(null)
    setSorts([])
    setPage(1)
    
    // clear everything from URL including legacy
    setSearchParams(new URLSearchParams(), { replace: true })
    
    // We can't rely on loadData getting the new URL instantly in the same cycle if we use legacy,
    // so we force a reload or rely on the effect. We'll rely on handleRun() manually fetching but with empty.
    setTimeout(() => {
      setLoading(true)
      getTickets({ page: 1, page_size: pageSize }).then(r => {
        setTickets(r.data.tickets || [])
        setTotal(r.data.total || 0)
        setTotalPages(r.data.total_pages || 1)
        setError('')
      }).finally(() => setLoading(false))
    }, 0)
  }

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage)
      syncToUrl(ast, sorts, newPage)
    }
  }

  return (
    <div className="fade-up" style={{ paddingBottom: 60 }}>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text)' }}>Incident Investigation Workspace</h1>
          <p style={{ fontSize: 13, color: 'var(--text2)', marginTop: 4 }}>Construct advanced queries, filter, and inspect ticket intelligence</p>
        </div>
        <ExportMenu ast={ast} sorts={sorts} />
      </div>

      <FilterBuilder 
        ast={ast} 
        onChange={setAst} 
        onRun={handleRun}
        onClear={handleClear}
        ciList={ciList}
        groupList={groupList}
      />
      
      {ast && ast.conditions.length > 0 && (
        <Card style={{ marginBottom: 20, padding: 16 }}>
          <SortBuilder sorts={sorts} onChange={setSorts} />
          {sorts && sorts.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <button onClick={handleRun} className="btn-primary" style={{ fontSize: 12, padding: '6px 14px' }}>Apply Sort</button>
            </div>
          )}
        </Card>
      )}

      {error ? (
        <Empty msg={error} />
      ) : loading ? (
        <Loader />
      ) : tickets.length === 0 ? (
        <Empty msg="No tickets match the current filter." />
      ) : (
        <Card style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontSize: 13, color: 'var(--text2)', fontWeight: 500 }}>
              Showing {((page - 1) * pageSize) + 1} - {Math.min(page * pageSize, total)} of {total.toLocaleString()} tickets
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
                  {['ID', 'Short Description', '3R Category', 'Cluster', 'CI', 'Priority', 'Status', 'Date'].map(h => (
                    <th key={h} style={{ textAlign: 'left', padding: '10px 12px', color: 'var(--text2)', fontWeight: 500, fontSize: 11, whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tickets.map(t => (
                  <tr 
                    key={t.ticket_id} 
                    className="data-row" 
                    style={{ borderBottom: '1px solid var(--border)', cursor: 'pointer' }}
                    onClick={() => setSelectedTicket(t)}
                  >
                    <td style={td}>
                      <span style={{ fontFamily: 'monospace', fontSize: 11, color: 'var(--accent-h)' }}>{t.ticket_id}</span>
                    </td>
                    <td style={{ ...td, maxWidth: 280, fontWeight: 500 }}>
                      <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {t.short_description}
                      </div>
                    </td>
                    <td style={td}><Badge color={t.three_r_category === 'RUNNER' ? 'var(--red)' : t.three_r_category === 'REPEATER' ? 'var(--amber)' : t.three_r_category === 'RARE' ? 'var(--purple)' : 'var(--text2)'}>{t.three_r_category || 'UNCLASSIFIED'}</Badge></td>
                    <td style={{ ...td, maxWidth: 180 }}>
                      <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        <Badge color={t.cluster_id === -1 ? 'var(--amber)' : 'var(--accent)'}>
                          {t.cluster_name || (t.cluster_id === -1 ? 'Noise' : `Cluster ${t.cluster_id}`)}
                        </Badge>
                      </div>
                    </td>
                    <td style={{ ...td }}>{t.ci_name || '—'}</td>
                    <td style={td}><PriorityBadge p={t.priority} /></td>
                    <td style={td}>{t.status || '—'}</td>
                    <td style={{ ...td, color: 'var(--text2)', whiteSpace: 'nowrap' }}>{t.created_date || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {selectedTicket && (
        <TicketDrawer ticket={selectedTicket} onClose={() => setSelectedTicket(null)} />
      )}
    </div>
  )
}

function PriorityBadge({ p }) {
  const colors = { Critical: 'var(--red)', High: 'var(--amber)', Medium: 'var(--blue)', Low: 'var(--green)' }
  const color = colors[p] || 'var(--text2)'
  return p ? <Badge color={color}>{p}</Badge> : <span style={{ color: 'var(--text2)' }}>—</span>
}

const td = { padding: '10px 12px', fontSize: 12 }

function Loader() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {Array.from({ length: 12 }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height: 44, borderRadius: i === 0 ? '12px 12px 0 0' : i === 11 ? '0 0 12px 12px' : 0 }} />
      ))}
    </div>
  )
}

function Empty({ msg }) {
  return (
    <div style={{ textAlign: 'center', padding: '80px 20px', color: 'var(--text2)' }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>🎫</div>
      <div style={{ fontSize: 15, fontWeight: 500, color: 'var(--text)', marginBottom: 8 }}>No Tickets</div>
      <div style={{ fontSize: 13 }}>{msg}</div>
    </div>
  )
}
