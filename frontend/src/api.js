import axios from 'axios'

// In dev: Vite proxies /api → http://localhost:8000 (vite.config.js)
// In prod: VITE_API_URL is set to the Render backend URL
const baseURL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api'

const api = axios.create({
  baseURL,
  timeout: 30000,
})

export const uploadCSV     = (file)        => { const fd = new FormData(); fd.append('file', file); return api.post('/upload', fd) }
export const loadSample    = ()            => api.post('/load-sample', {}, { timeout: 30000 })
export const getStatus     = ()            => api.get('/status',    { timeout: 10000 })
export const getDashboard  = ()            => api.get('/dashboard')
export const getClusters   = ()            => api.get('/clusters')
export const getTickets    = (params)      => api.get('/tickets',   { params })
export const getCIList     = ()            => api.get('/ci-list')
export const getCIClusters = (ci_name)     => api.get('/ci-clusters', { params: { ci_name } })
export const getGroupList     = ()            => api.get('/group-list')
export const getGroupClusters = (group_name) => api.get('/group-clusters', { params: { group_name } })
export const getClusterDetail = (id)          => api.get(`/clusters/${id}`)
export const predictTicket = (description) => api.post('/predict',  { description })
export const clearData     = ()            => api.delete('/clear')
export const getHealth     = ()            => api.get('/health',    { timeout: 10000 })
export const warmup        = ()            => api.get('/warmup',    { timeout: 120000 })
export const getJobs       = (params)      => api.get('/jobs',      { params })
export const getJob        = (id)          => api.get(`/jobs/${id}`)
export const cancelJob     = (id)          => api.post(`/jobs/${id}/cancel`)
export const getServiceNowGroups = ()      => api.get('/servicenow-groups')
export const importServiceNow    = (params) => api.post('/servicenow-import', {}, { params })
