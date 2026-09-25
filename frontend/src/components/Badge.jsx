export default function Badge({ children, color = 'var(--accent)', size = 'sm' }) {
  const pad = size === 'sm' ? '2px 8px' : '4px 12px'
  const fs = size === 'sm' ? 11 : 12
  return (
    <span style={{
      display: 'inline-block',
      background: color + '20',
      color,
      padding: pad,
      borderRadius: 20,
      fontSize: fs,
      fontWeight: 600,
      whiteSpace: 'nowrap',
    }}>
      {children}
    </span>
  )
}
