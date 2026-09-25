export const THEMES = {
  dark: {
    '--bg':        '#06080f',
    '--surface':   '#0b0f1c',
    '--surface2':  '#101528',
    '--border':    '#1a2240',
    '--border2':   '#223060',
    '--accent':    '#0f62fe',
    '--accent-h':  '#4589ff',
    '--accent-bg': 'rgba(15,98,254,0.10)',
    '--purple':    '#7c3aed',
    '--purple-h':  '#a78bfa',
    '--purple-bg': 'rgba(124,58,237,0.10)',
    '--green':     '#22c55e',
    '--green-bg':  'rgba(34,197,94,0.10)',
    '--red':       '#f43f5e',
    '--red-bg':    'rgba(244,63,94,0.10)',
    '--amber':     '#f59e0b',
    '--amber-bg':  'rgba(245,158,11,0.10)',
    '--blue':      '#38bdf8',
    '--blue-bg':   'rgba(56,189,248,0.10)',
    '--text':      '#e2e8f0',
    '--text2':     '#8899bb',
    '--text3':     '#3d4f70',
    '--muted':     '#8899bb',
    '--success':   '#22c55e',
    '--accent2':   '#f59e0b',
    '--shadow':    '0 4px 24px rgba(0,0,0,0.5)',
  },
  light: {
    '--bg':        '#f0f4f8',
    '--surface':   '#ffffff',
    '--surface2':  '#f5f8fc',
    '--border':    '#d6e0ee',
    '--border2':   '#b0c4de',
    '--accent':    '#0f62fe',
    '--accent-h':  '#0043ce',
    '--accent-bg': 'rgba(15,98,254,0.08)',
    '--purple':    '#7c3aed',
    '--purple-h':  '#5b21b6',
    '--purple-bg': 'rgba(124,58,237,0.08)',
    '--green':     '#16a34a',
    '--green-bg':  'rgba(22,163,74,0.08)',
    '--red':       '#e11d48',
    '--red-bg':    'rgba(225,29,72,0.08)',
    '--amber':     '#d97706',
    '--amber-bg':  'rgba(217,119,6,0.08)',
    '--blue':      '#0284c7',
    '--blue-bg':   'rgba(2,132,199,0.08)',
    '--text':      '#0f172a',
    '--text2':     '#475569',
    '--text3':     '#94a3b8',
    '--muted':     '#475569',
    '--success':   '#16a34a',
    '--accent2':   '#d97706',
    '--shadow':    '0 4px 24px rgba(0,0,0,0.08)',
  },
}

export const THEME_META = {
  dark:  { label: 'Dark',  icon: '🌙' },
  light: { label: 'Light', icon: '☀️' },
}

export function applyTheme(name) {
  const vars = THEMES[name]
  if (!vars) return
  const root = document.documentElement
  Object.entries(vars).forEach(([k, v]) => root.style.setProperty(k, v))
  localStorage.setItem('ticketiq-theme', name)
}

export function getSavedTheme() {
  return localStorage.getItem('ticketiq-theme') || 'dark'
}
