import { NavLink, useNavigate } from 'react-router-dom'

import {
  LayoutDashboard,
  Layers,
  Monitor,
  Ticket,
  Trash2,
  Upload,
  Download,
  Play,
  Users,
  Clock,
} from 'lucide-react'

import { clearData } from '../api'


const NAV = [
  {
    to: '/dashboard',
    icon: LayoutDashboard,
    label: 'Dashboard',
  },
  {
    to: '/clusters',
    icon: Layers,
    label: 'Clusters',
  },
  {
    to: '/ci',
    icon: Monitor,
    label: 'CI Analysis',
  },
  {
    to: '/groups',
    icon: Users,
    label: 'Assigned Groups',
  },
  {
    to: '/tickets',
    icon: Ticket,
    label: 'Tickets',
  },
  {
    to: '/jobs',
    icon: Clock,
    label: 'Job History',
  },
]


export default function Sidebar({
  onUpload,
  processing,
  onSampleLoad,
  theme,
  onClearData,
}) {

  // Used for navigation
  const navigate = useNavigate()


  // ==========================================================
  // CLEAR ALL DATA
  // ==========================================================

  async function handleClear() {

    // Confirmation
    if (!confirm('Clear all uploaded data and reset?')) {
      return
    }

    try {
      // Clear data from backend
      await clearData()

      // Call onClearData to update App state (toast and state clear)
      if (onClearData) {
        onClearData()
      }
      
      // Navigate to Home page
      navigate('/home')

    } catch (error) {
      console.error('Failed to clear data:', error)
      const errorMsg = error.response?.data?.detail || 'Failed to clear data. Please try again.'
      alert(errorMsg)
    }
  }


  // ==========================================================
  // LOAD SAMPLE DATA
  // ==========================================================

  function handleLoadSample() {

    if (processing) {
      return
    }

    // Directly call backend
    // Backend reads sample_tickets.csv
    // from its own disk
    if (onSampleLoad) {
      onSampleLoad()
    }
  }


  // ==========================================================
  // SIDEBAR
  // ==========================================================

  return (
    <aside
      style={{
        width: 200,
        minHeight: '100vh',
        background: 'var(--surface)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        top: 0,
        left: 0,
        bottom: 0,
        zIndex: 100,
      }}
    >

      {/* ====================================================
          LOGO BAR
      ==================================================== */}

      <div
        style={{
          padding: '0 20px',
          height: 64,
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          flexDirection: 'column',
          justifyContent: 'center',
        }}
      >

        <div
          style={{
            fontWeight: 700,
            fontSize: 25,
            color: 'var(--text)',
            letterSpacing: '-0.02em',
            lineHeight: 1.2,
          }}
        >
          3R Analyzer
        </div>

        <div
          style={{
            fontSize: 10,
            color: 'var(--text2)',
            marginTop: 2,
          }}
        >
          AI Intelligence Platform
        </div>

      </div>


      {/* ====================================================
          NAVIGATION
      ==================================================== */}

      <nav
        style={{
          flex: 1,
          padding: '14px 10px',
        }}
      >

        <div
          style={{
            fontSize: 10,
            fontWeight: 600,
            color: 'var(--text3)',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            padding: '4px 10px 10px',
          }}
        >
          Navigation
        </div>


        {NAV.map(
          ({
            to,
            icon: Icon,
            label,
          }) => (

            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className="nav-link"

              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '9px 12px',
                borderRadius: 8,

                color: isActive
                  ? (
                      theme === 'yellow'
                        ? '#1a1a1a'
                        : '#fff'
                    )
                  : 'var(--text2)',

                background: isActive
                  ? 'var(--accent)'
                  : 'transparent',

                fontWeight: isActive
                  ? 600
                  : 400,

                fontSize: 13.5,

                marginBottom: 3,

                border: '1px solid transparent',

                boxShadow: isActive
                  ? '0 2px 12px var(--accent-bg)'
                  : 'none',
              })}
            >

              <Icon size={15} />

              {label}

            </NavLink>

          )
        )}

      </nav>


      {/* ====================================================
          ACTIONS
      ==================================================== */}

      <div
        style={{
          padding: '12px 12px 18px',
          borderTop: '1px solid var(--border)',
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
        }}
      >

        {/* ==================================================
            UPLOAD CSV
        ================================================== */}

        <label
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,

            background: processing
              ? 'var(--surface2)'
              : 'linear-gradient(135deg, var(--accent), var(--purple))',

            color: processing
              ? 'var(--text2)'
              : (
                  theme === 'yellow'
                    ? '#1a1a1a'
                    : '#fff'
                ),

            padding: '10px 14px',
            borderRadius: 9,

            cursor: processing
              ? 'not-allowed'
              : 'pointer',

            fontSize: 13,
            fontWeight: 600,

            transition: 'opacity 0.15s',

            boxShadow: processing
              ? 'none'
              : '0 2px 14px rgba(15,98,254,0.35)',
          }}
        >

          <Upload size={14} />

          {processing
            ? 'Processing…'
            : 'Upload File'
          }

          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            style={{
              display: 'none',
            }}
            disabled={processing}
            onChange={e => {

              const file =
                e.target.files[0]

              if (file) {
                onUpload(file)
              }

            }}
          />

        </label>


        {/* ==================================================
            CLEAR ALL DATA
        ================================================== */}

        <button
          onClick={handleClear}
          className="btn-ghost"
          style={{
            justifyContent: 'center',
            fontSize: 12,
          }}
        >

          <Trash2 size={13} />

          Clear All Data

        </button>


        {/* ==================================================
            LOAD SAMPLE DATA
        ================================================== */}

        <button
          onClick={handleLoadSample}
          disabled={processing}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 6,

            background: 'var(--green-bg)',

            border:
              '1px solid rgba(34,197,94,0.3)',

            color: 'var(--green)',

            padding: '9px',

            borderRadius: 9,

            fontSize: 12,

            fontWeight: 600,

            cursor: processing
              ? 'not-allowed'
              : 'pointer',

            transition: 'all 0.15s',

            opacity: processing
              ? 0.5
              : 1,

            fontFamily: 'inherit',
          }}
        >

          <Play size={13} />

          Load Sample Data (5,000 tickets)

        </button>


        {/* ==================================================
            DOWNLOAD SAMPLE CSV
        ================================================== */}

        <a
          href="/api/download-sample"
          download

          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 6,

            border:
              '1px solid var(--border)',

            color: 'var(--text2)',

            padding: '8px',

            borderRadius: 9,

            fontSize: 12,

            fontWeight: 500,

            textDecoration: 'none',

            transition: 'all 0.15s',

            background: 'transparent',
          }}

          onMouseEnter={e => {
            e.currentTarget.style.borderColor =
              'var(--accent)'

            e.currentTarget.style.color =
              'var(--accent)'
          }}

          onMouseLeave={e => {
            e.currentTarget.style.borderColor =
              'var(--border)'

            e.currentTarget.style.color =
              'var(--text2)'
          }}
        >

          <Download size={13} />

          Download Sample CSV

        </a>

      </div>

    </aside>
  )
}