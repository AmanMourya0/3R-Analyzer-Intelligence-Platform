export default function StatCard({ label, value, icon: Icon, color = 'var(--accent)', bg = 'var(--accent-bg)', sub, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '20px 22px',
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        cursor: onClick ? 'pointer' : undefined,
        transition: 'border-color 0.15s, box-shadow 0.15s',
      }}
      onMouseEnter={onClick ? e => {
        e.currentTarget.style.borderColor = color
        e.currentTarget.style.boxShadow = `0 4px 20px ${color}20`
      } : undefined}
      onMouseLeave={onClick ? e => {
        e.currentTarget.style.borderColor = 'var(--border)'
        e.currentTarget.style.boxShadow = 'none'
      } : undefined}
    >
      {Icon && (
        <div style={{
          width: 44, height: 44, borderRadius: 10,
          background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0,
        }}>
          <Icon size={20} color={color} />
        </div>
      )}
      <div>
        <div style={{ fontSize: 11, color: 'var(--text2)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>{label}</div>
        <div style={{ fontSize: 26, fontWeight: 700, color: 'var(--text)', lineHeight: 1 }}>{value}</div>
        {sub && <div style={{ fontSize: 11, color: 'var(--text2)', marginTop: 4 }}>{sub}</div>}
      </div>
    </div>
  )
}
