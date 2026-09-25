export function SkeletonLine({ w = '100%', h = 14, mb = 0 }) {
  return <div className="skeleton" style={{ width: w, height: h, marginBottom: mb }} />
}

export function SkeletonCard({ h = 120 }) {
  return (
    <div style={{
      background: 'var(--surface)', border: '1px solid var(--border)',
      borderRadius: 'var(--radius)', padding: 20, height: h,
    }}>
      <SkeletonLine w="40%" h={12} mb={12} />
      <SkeletonLine w="60%" h={28} mb={8} />
      <SkeletonLine w="30%" h={10} />
    </div>
  )
}

export function SkeletonTable({ rows = 6 }) {
  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', overflow: 'hidden' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', display: 'flex', gap: 16 }}>
        {[120, 200, 150, 80, 80].map((w, i) => <SkeletonLine key={i} w={w} h={11} />)}
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', display: 'flex', gap: 16 }}>
          {[80, 180, 140, 70, 70].map((w, j) => <SkeletonLine key={j} w={w} h={12} />)}
        </div>
      ))}
    </div>
  )
}
