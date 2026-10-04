import { useEffect, useState, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getTickets, getClusters, getCIList, getGroupList } from '../api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import FilterBuilder from '../components/FilterBuilder'
import SortBuilder from '../components/SortBuilder'
import TicketDrawer from '../components/TicketDrawer'
import ExportMenu from '../components/ExportMenu'
import ColumnSelector from '../components/ColumnSelector'
import { ChevronLeft, ChevronRight } from 'lucide-react'

const ticketColumns = [
  { key: 'incident_number', label: 'INCIDENT NUMBER', required: true, defaultVisible: true },
  { key: 'caller', label: 'CALLER', defaultVisible: false },
  { key: 'assignment_group', label: 'ASSIGNMENT GROUP', defaultVisible: false },
  { key: 'created_date', label: 'CREATED', defaultVisible: true },
  { key: 'short_description', label: 'SHORT DESCRIPTION', required: true, defaultVisible: true },
  { key: 'description', label: 'DESCRIPTION', defaultVisible: true },
  { key: 'category', label: 'CATEGORY', defaultVisible: false },
  { key: 'three_r_category', label: '3R CATEGORY', defaultVisible: true },
  { key: 'cluster_name', label: 'CLUSTER', defaultVisible: true },
  { key: 'priority', label: 'PRIORITY', defaultVisible: true },
  { key: 'state', label: 'STATE', defaultVisible: true },
  { key: 'assigned_to', label: 'ASSIGNED TO', defaultVisible: false },
  { key: 'resolved_by', label: 'RESOLVED BY', defaultVisible: false },
  { key: 'resolved_date', label: 'RESOLVED', defaultVisible: false },
  { key: 'kb_number', label: 'KB NUMBER', defaultVisible: false },
  { key: 'it_batch_job', label: 'IT BATCH JOB', defaultVisible: false },
  { key: 'reassignment_count', label: 'REASSIGNMENT COUNT', defaultVisible: false },
  { key: 'configuration_item', label: 'CONFIGURATION ITEM', defaultVisible: true },
  { key: 'offending_ci', label: 'OFFENDING CI', defaultVisible: false },
  { key: 'offending_ci_category', label: 'OFFENDING CI CATEGORY', defaultVisible: false },
  { key: 'cluster_id', label: 'CLUSTER ID', defaultVisible: false },
  { key: 'problem_candidate', label: 'PROBLEM CANDIDATE', defaultVisible: false },
]

export default function Tickets() {
  const [searchParams, setSearchParams] = useSearchParams()
  
  // Parse state from URL or Local Storage
  const urlFilterStr = searchParams.get('filter')
  const urlSortStr = searchParams.get('sort')
  const initialPage = parseInt(searchParams.get('page') || '1', 10)

  const FILTER_KEY = '3r_workspace_filter'
  const SORT_KEY = '3r_workspace_sort'

  const initialFilterStr = urlFilterStr !== null ? urlFilterStr : (localStorage.getItem(FILTER_KEY) || '')
  let initialAst = null
  try { if (initialFilterStr) initialAst = JSON.parse(decodeURIComponent(initialFilterStr)) } catch(e) {}
  
  const initialSortStr = urlSortStr !== null ? urlSortStr : (localStorage.getItem(SORT_KEY) || '')
  let initialSorts = []
  try { if (initialSortStr) initialSorts = JSON.parse(decodeURIComponent(initialSortStr)) } catch(e) {}
  
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
  
  const [visibleCols, setVisibleCols] = useState(ticketColumns.map(c => c.key))

  useEffect(() => {
    Promise.all([getCIList(), getGroupList()])
      .then(([cir, gr]) => {
        setCiList(cir.data.ci_list || [])
        setGroupList(gr.data.group_list || [])
      })
      .catch(() => {})
  }, [])

  // Sync state to URL and Local Storage when filters change
  const syncToUrl = useCallback((newAst, newSorts, newPage) => {
    const newParams = new URLSearchParams(searchParams)
    
    if (newAst && newAst.conditions && newAst.conditions.length > 0) {
      const val = encodeURIComponent(JSON.stringify(newAst))
      newParams.set('filter', val)
      localStorage.setItem(FILTER_KEY, val)
    } else {
      newParams.delete('filter')
      localStorage.removeItem(FILTER_KEY)
    }
    
    if (newSorts && newSorts.length > 0) {
      const val = encodeURIComponent(JSON.stringify(newSorts))
      newParams.set('sort', val)
      localStorage.setItem(SORT_KEY, val)
    } else {
      newParams.delete('sort')
      localStorage.removeItem(SORT_KEY)
    }
    
    if (newPage > 1) {
      newParams.set('page', newPage)
    } else {
      newParams.delete('page')
    }
    
    setSearchParams(newParams, { replace: true })
  }, [searchParams, setSearchParams])

  // Initial sync from localStorage to URL if URL lacked params
  useEffect(() => {
    if (urlFilterStr === null && localStorage.getItem(FILTER_KEY)) {
       syncToUrl(initialAst, initialSorts, initialPage)
    } else if (urlSortStr === null && localStorage.getItem(SORT_KEY)) {
       syncToUrl(initialAst, initialSorts, initialPage)
    }
  }, [])

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
    localStorage.removeItem(FILTER_KEY)
    localStorage.removeItem(SORT_KEY)
    
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
        <div style={{ display: 'flex', gap: 8 }}>
          <ColumnSelector 
            columns={ticketColumns} 
            tableKey="tickets" 
            onColumnChange={setVisibleCols} 
          />
          <ExportMenu ast={ast} sorts={sorts} />
        </div>
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
                  {ticketColumns.filter(c => visibleCols.includes(c.key)).map(c => (
                    <th key={c.key} style={{ textAlign: 'left', padding: '10px 12px', color: 'var(--text2)', fontWeight: 500, fontSize: 11, whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{c.label}</th>
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
                    {ticketColumns.map(col => {
                      if (!visibleCols.includes(col.key)) return null;

                      switch (col.key) {
                        case 'incident_number':
                          return (
                            <td key={col.key} style={td}>
                              <span style={{ fontFamily: 'monospace', fontSize: 11, color: 'var(--accent-h)' }}>{t.incident_number || t.ticket_id}</span>
                            </td>
                          );
                        case 'short_description':
                          return (
                            <td key={col.key} style={{ ...td, maxWidth: 280, fontWeight: 500 }}>
                              <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {t.short_description}
                              </div>
                            </td>
                          );
                        case 'description':
                          return (
                            <td key={col.key} style={{ ...td, maxWidth: 300 }}>
                              <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {t.description || '—'}
                              </div>
                            </td>
                          );
                        case 'three_r_category':
                          return (
                            <td key={col.key} style={td}>
                              <Badge color={t.three_r_category === 'RUNNER' ? 'var(--red)' : t.three_r_category === 'REPEATER' ? 'var(--amber)' : t.three_r_category === 'RARE' ? 'var(--purple)' : 'var(--text2)'}>
                                {t.three_r_category || 'UNCLASSIFIED'}
                              </Badge>
                            </td>
                          );
                        case 'cluster_name':
                          return (
                            <td key={col.key} style={{ ...td, maxWidth: 180 }}>
                              <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                <Badge color={t.cluster_id === -1 ? 'var(--amber)' : 'var(--accent)'}>
                                  {t.cluster_name || (t.cluster_id === -1 ? 'Noise' : `Cluster ${t.cluster_id}`)}
                                </Badge>
                              </div>
                            </td>
                          );
                        case 'priority':
                          return <td key={col.key} style={td}><PriorityBadge p={t.priority} /></td>;
                        case 'state':
                          return <td key={col.key} style={td}>{t.state || t.status || '—'}</td>;
                        case 'created_date':
                        case 'resolved_date':
                          return <td key={col.key} style={{ ...td, color: 'var(--text2)', whiteSpace: 'nowrap' }}>{t[col.key] || '—'}</td>;
                        case 'problem_candidate':
                          return <td key={col.key} style={td}>{t.problem_candidate ? 'Yes' : 'No'}</td>;
                        case 'configuration_item':
                          return <td key={col.key} style={{ ...td }}>{t.configuration_item || t.ci_name || '—'}</td>;
                        case 'assignment_group':
                          return <td key={col.key} style={{ ...td }}>{t.assignment_group || t.assigned_group || '—'}</td>;
                        default:
                          return <td key={col.key} style={{ ...td }}>{t[col.key] !== null && t[col.key] !== undefined ? String(t[col.key]) : '—'}</td>;
                      }
                    })}
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
