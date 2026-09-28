with open("frontend/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

offline_screen = """
  if (offline) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)', color: 'var(--text)' }}>
        <div style={{ textAlign: 'center' }}>
          <AlertCircle size={48} color="var(--red)" style={{ marginBottom: 16 }} />
          <h2>Platform Maintenance</h2>
          <p style={{ color: 'var(--text2)' }}>The 3R Analyzer Intelligence backend is currently unavailable.</p>
        </div>
      </div>
    )
  }
"""

content = content.replace('const [serverReady, setServerReady] = useState(false)', 'const [serverReady, setServerReady] = useState(false)\n  const [offline, setOffline] = useState(false)')

old_ping = """    let attempts = 0
    function ping() {
      getHealth()
        .then(r => {
          setServerReady(true)
          setDataLoaded(r.data.data_loaded)
          warmup().catch(() => {})
        })
        .catch(() => { if (++attempts < 20) setTimeout(ping, 3000) })
    }"""

new_ping = """    let attempts = 0
    function ping() {
      getHealth()
        .then(r => {
          setServerReady(true)
          setOffline(false)
          setDataLoaded(r.data.data_loaded)
          warmup().catch(() => {})
        })
        .catch(() => { 
            if (++attempts < 3) setTimeout(ping, 3000) 
            else setOffline(true)
        })
    }"""

content = content.replace(old_ping, new_ping)

old_return = """  return (
    <BrowserRouter>"""
new_return = offline_screen + """  return (
    <BrowserRouter>"""

content = content.replace(old_return, new_return)

with open("frontend/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
