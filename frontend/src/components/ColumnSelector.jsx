import { useState, useRef, useEffect } from 'react'
import { Settings2, Check } from 'lucide-react'

export default function ColumnSelector({ columns, tableKey, onColumnChange }) {
  const [isOpen, setIsOpen] = useState(false)
  
  const storageKey = `3r-analyzer:${tableKey}:visible-columns`

  const getInitialCols = () => {
    try {
      const saved = localStorage.getItem(storageKey)
      if (saved) {
        const parsed = JSON.parse(saved)
        // ensure required are always included
        const required = columns.filter(c => c.required).map(c => c.key)
        return Array.from(new Set([...parsed, ...required]))
      }
    } catch(e) {}
    return columns.filter(c => c.defaultVisible !== false).map(c => c.key)
  }

  const [visible, setVisible] = useState(getInitialCols)
  const menuRef = useRef(null)

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(visible))
    onColumnChange(visible)
  }, [visible, storageKey, onColumnChange])

  useEffect(() => {
    const handleClick = e => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    if (isOpen) document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [isOpen])

  const handleToggle = (col) => {
    if (col.required) return
    setVisible(prev => 
      prev.includes(col.key) 
        ? prev.filter(k => k !== col.key)
        : [...prev, col.key]
    )
  }

  const handleSelectAll = () => {
    setVisible(columns.map(c => c.key))
  }

  const handleDeselectAll = () => {
    setVisible(columns.filter(c => c.required).map(c => c.key))
  }

  const handleReset = () => {
    setVisible(columns.filter(c => c.defaultVisible !== false).map(c => c.key))
  }

  return (
    <div style={{ position: 'relative' }} ref={menuRef}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          color: 'var(--text)',
          padding: '6px 12px',
          borderRadius: 8,
          fontSize: 12,
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'background 0.15s'
        }}
        onMouseOver={e => e.target.style.background = 'var(--surface2)'}
        onMouseOut={e => e.target.style.background = 'var(--surface)'}
      >
        <Settings2 size={14} />
        Columns ▾
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute',
          top: '100%',
          right: 0,
          marginTop: 8,
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          boxShadow: 'var(--shadow)',
          borderRadius: 8,
          width: 240,
          zIndex: 100,
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{ 
            padding: '8px 12px', 
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            gap: 8,
            fontSize: 11
          }}>
            <button 
              onClick={handleSelectAll}
              style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', padding: 0 }}
            >All</button>
            <span style={{ color: 'var(--border)' }}>|</span>
            <button 
              onClick={handleDeselectAll}
              style={{ background: 'none', border: 'none', color: 'var(--text2)', cursor: 'pointer', padding: 0 }}
            >None</button>
            <span style={{ color: 'var(--border)' }}>|</span>
            <button 
              onClick={handleReset}
              style={{ background: 'none', border: 'none', color: 'var(--text2)', cursor: 'pointer', padding: 0 }}
            >Reset</button>
          </div>
          
          <div style={{ maxHeight: 300, overflowY: 'auto', padding: '6px 0' }}>
            {columns.map(col => (
              <label 
                key={col.key}
                onClick={(e) => {
                  e.preventDefault()
                  handleToggle(col)
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '6px 12px',
                  cursor: col.required ? 'not-allowed' : 'pointer',
                  opacity: col.required ? 0.6 : 1,
                  fontSize: 13,
                  color: 'var(--text)'
                }}
                onMouseOver={e => { if (!col.required) e.currentTarget.style.background = 'var(--surface2)' }}
                onMouseOut={e => { if (!col.required) e.currentTarget.style.background = 'transparent' }}
              >
                <div style={{
                  width: 16, height: 16, 
                  borderRadius: 4, 
                  border: `1px solid ${visible.includes(col.key) ? 'var(--accent)' : 'var(--border)'}`,
                  background: visible.includes(col.key) ? 'var(--accent)' : 'transparent',
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  {visible.includes(col.key) && <Check size={12} color="#fff" />}
                </div>
                {col.label}
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
