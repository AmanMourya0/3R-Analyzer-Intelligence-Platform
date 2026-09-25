import { useState, useEffect } from 'react'
import { Upload, Database, Calendar, Users } from 'lucide-react'
import { applyTheme } from '../theme'


// ============================================================
// CSV PARSER
// ============================================================

function parseCSV(text) {
  const lines = text.trim().split('\n')

  if (!lines.length) {
    return []
  }

  const headers = lines[0]
    .split(',')
    .map(h => h.trim().replace(/^"|"$/g, ''))

  return lines.slice(1).map(line => {
    const vals = line
      .split(',')
      .map(v => v.trim().replace(/^"|"$/g, ''))

    return Object.fromEntries(
      headers.map((h, i) => [h, vals[i] || ''])
    )
  })
}


// ============================================================
// CSV GENERATOR
// ============================================================

function toCSV(rows) {
  if (!rows.length) {
    return ''
  }

  const headers = Object.keys(rows[0])

  const lines = [headers.join(',')]

  rows.forEach(row => {
    lines.push(
      headers
        .map(header => {
          const value = row[header] || ''
          return `"${value.replace(/"/g, '""')}"`
        })
        .join(',')
    )
  })

  return lines.join('\n')
}


// ============================================================
// HOME PAGE
// ============================================================

export default function Home({
  onUpload,
  processing,
  theme,
  setTheme,
}) {
  const [dragOver, setDragOver] = useState(false)
  const [fileName, setFileName] = useState('')


  // ----------------------------------------------------------
  // Handle uploaded file
  // ----------------------------------------------------------

  function handleFile(file) {
    if (!file) {
      return
    }

    setFileName(file.name)

    onUpload(file)
  }


  // ----------------------------------------------------------
  // HOME PAGE
  // ----------------------------------------------------------

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--bg)',
      }}
    >

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div
        style={{
          height: 56,
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 32px',
          background: 'var(--surface)',
          flexShrink: 0,
        }}
      >

        {/* Logo / Title */}

        <div>
          <div
            style={{
              fontWeight: 700,
              fontSize: 15,
              color: 'var(--text)',
              letterSpacing: '-0.01em',
              lineHeight: 1.2,
            }}
          >
            3R Analyzer
          </div>

          <div
            style={{
              fontSize: 10,
              color: 'var(--text2)',
            }}
          >
            AI Intelligence Platform
          </div>
        </div>


        {/* Theme Button */}

        <button
          onClick={() => {
            const newTheme =
              theme === 'dark' ? 'light' : 'dark'

            applyTheme(newTheme)

            if (setTheme) {
              setTheme(newTheme)
            }
          }}
          style={{
            width: 36,
            height: 36,
            borderRadius: 10,
            border: '1px solid var(--border)',
            background: 'var(--surface2)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 17,
          }}
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>

      </div>


      {/* ======================================================
          MAIN CONTENT
      ====================================================== */}

      <div
        style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          padding: '0 80px',
          gap: 80,
        }}
      >

        {/* ====================================================
            LEFT SIDE — BRANDING
        ==================================================== */}

        <div
          style={{
            flex: 1,
            maxWidth: 480,
          }}
        >

          {/* Badge */}

          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              background: 'var(--accent-bg)',
              border: '1px solid rgba(15,98,254,0.2)',
              borderRadius: 20,
              padding: '5px 12px',
              marginBottom: 24,
            }}
          >
            <span style={{ fontSize: 13 }}>
              ✨
            </span>

            <span
              style={{
                fontSize: 11,
                fontWeight: 600,
                color: 'var(--accent)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
              }}
            >
              AI-Powered IT Intelligence
            </span>
          </div>


          {/* Main Heading */}

          <h1
            style={{
              fontSize: 44,
              fontWeight: 800,
              color: 'var(--text)',
              lineHeight: 1.1,
              marginBottom: 12,
              letterSpacing: '-0.03em',
            }}
          >
            3R Analyzer
          </h1>


          {/* Sub Heading */}

          <h2
            style={{
              fontSize: 22,
              fontWeight: 600,
              color: 'var(--accent)',
              marginBottom: 18,
            }}
          >
            Transform your IT support with AI
          </h2>


          {/* Description */}

          <p
            style={{
              fontSize: 14,
              color: 'var(--text2)',
              lineHeight: 1.7,
              marginBottom: 36,
            }}
          >
            Automatically cluster recurring tickets, discover
            hidden patterns, and reduce resolution time. Make
            data-driven decisions with powerful AI insights.
          </p>


          {/* Feature Cards */}

          <div
            style={{
              display: 'flex',
              gap: 20,
            }}
          >

            {[
              {
                icon: '🧩',
                label: 'Smart Clustering',
                sub: 'AI-powered grouping',
              },
              {
                icon: '🔍',
                label: 'Pattern Detection',
                sub: 'Identify root causes',
              },
              {
                icon: '⚡',
                label: 'Faster Resolution',
                sub: 'Reduce ticket volume',
              },
            ].map(feature => (
              <div
                key={feature.label}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  minWidth: 0,
                }}
              >

                <div
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 10,
                    background: 'var(--accent-bg)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 16,
                    flexShrink: 0,
                  }}
                >
                  {feature.icon}
                </div>

                <div
                  style={{
                    minWidth: 0,
                  }}
                >
                  <div
                    style={{
                      fontSize: 13,
                      fontWeight: 700,
                      color: 'var(--text)',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {feature.label}
                  </div>

                  <div
                    style={{
                      fontSize: 11,
                      color: 'var(--text2)',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {feature.sub}
                  </div>
                </div>

              </div>
            ))}

          </div>

        </div>


        {/* ====================================================
            RIGHT SIDE — CARDS
        ==================================================== */}

        <div
          style={{
            display: 'flex',
            gap: 20,
            flexShrink: 0,
          }}
        >

          {/* ==================================================
              UPLOAD CSV CARD
          ================================================== */}

          <div style={card}>

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                marginBottom: 6,
              }}
            >

              <div style={iconBox('var(--accent-bg)')}>
                <Upload
                  size={20}
                  color="var(--accent)"
                />
              </div>

              <span
                style={{
                  fontWeight: 700,
                  fontSize: 15,
                  color: 'var(--text)',
                }}
              >
                Upload CSV
              </span>

            </div>


            <p
              style={{
                fontSize: 12,
                color: 'var(--text2)',
                marginBottom: 20,
                lineHeight: 1.5,
              }}
            >
              Import tickets from a CSV file and start analyzing
              instantly.
            </p>


            {/* Drop Zone */}

            <label
              onDragOver={event => {
                event.preventDefault()
                setDragOver(true)
              }}

              onDragLeave={() => {
                setDragOver(false)
              }}

              onDrop={event => {
                event.preventDefault()
                setDragOver(false)

                const file = event.dataTransfer.files[0]

                if (file) {
                  handleFile(file)
                }
              }}

              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 6,
                padding: '24px 16px',
                borderRadius: 12,
                border: `2px dashed ${
                  dragOver
                    ? 'var(--accent)'
                    : 'var(--border2)'
                }`,
                background: dragOver
                  ? 'var(--accent-bg)'
                  : 'var(--surface2)',
                cursor: processing
                  ? 'not-allowed'
                  : 'pointer',
                marginBottom: 14,
                transition: 'all 0.15s',
              }}
            >

              <Upload
                size={22}
                color={
                  dragOver
                    ? 'var(--accent)'
                    : 'var(--text3)'
                }
              />

              <span
                style={{
                  fontSize: 13,
                  fontWeight: 500,
                  color: 'var(--text2)',
                }}
              >
                {fileName || 'Drag & drop your CSV file here'}
              </span>

              <span
                style={{
                  fontSize: 11,
                  color: 'var(--accent)',
                }}
              >
                or click to browse
              </span>


              <input
                type="file"
                accept=".csv"
                style={{ display: 'none' }}
                disabled={processing}
                onChange={event => {
                  handleFile(event.target.files[0])
                }}
              />

            </label>


            {/* Upload Button */}

            <button
              disabled={processing}
              onClick={() => {
                document
                  .querySelector('input[accept=".csv"]')
                  ?.click()
              }}
              style={primaryBtn('var(--accent)')}
            >
              {processing ? 'Processing...' : 'Upload CSV'}
            </button>

          </div>


          {/* ==================================================
              SERVICENOW CARD
          ================================================== */}

          <div style={card}>

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                marginBottom: 6,
              }}
            >

              <div style={iconBox('var(--purple-bg)')}>
                <Database
                  size={20}
                  color="var(--purple)"
                />
              </div>

              <span
                style={{
                  fontWeight: 700,
                  fontSize: 15,
                  color: 'var(--text)',
                }}
              >
                Import from ServiceNow
              </span>

            </div>


            <p
              style={{
                fontSize: 12,
                color: 'var(--text2)',
                marginBottom: 20,
                lineHeight: 1.5,
              }}
            >
              Connect and import tickets directly from ServiceNow.
            </p>


            <SNFilters
              onImport={file => {
                onUpload(file)
              }}
              processing={processing}
            />

          </div>

        </div>

      </div>

    </div>
  )
}


// ============================================================
// SERVICENOW FILTERS
// ============================================================

function SNFilters({
  onImport,
  processing,
}) {

  const [rows, setRows] = useState(null)

  const [groups, setGroups] = useState([])

  const [dateMin, setDateMin] = useState('')

  const [dateMax, setDateMax] = useState('')

  const [selectedGroup, setSelectedGroup] = useState('')

  const [dateFrom, setDateFrom] = useState('')

  const [dateTo, setDateTo] = useState('')

  const [loaded, setLoaded] = useState(false)

  const [loadErr, setLoadErr] = useState(false)


  // ----------------------------------------------------------
  // Load sample ServiceNow data
  // ----------------------------------------------------------

  function loadData() {

    if (loaded) {
      return
    }

    fetch('/sample_tickets.csv')

      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load sample CSV')
        }

        return response.text()
      })

      .then(text => {

        const parsed = parseCSV(text)

        setRows(parsed)


        // Assignment groups

        const groupList = [
          ...new Set(
            parsed
              .map(row => row.assigned_group)
              .filter(Boolean)
          ),
        ].sort()

        setGroups(groupList)


        // Dates

        const dates = parsed
          .map(row =>
            (row.created_date || '').slice(0, 10)
          )
          .filter(Boolean)
          .sort()


        const minDate = dates[0] || ''

        const maxDate =
          dates[dates.length - 1] || ''


        setDateMin(minDate)
        setDateMax(maxDate)

        setDateFrom(minDate)
        setDateTo(maxDate)

        setLoaded(true)
      })

      .catch(() => {
        setLoadErr(true)
      })
  }


  // ----------------------------------------------------------
  // Load data when component mounts
  // ----------------------------------------------------------

  useEffect(() => {
    loadData()
  }, [])


  // ----------------------------------------------------------
  // Calculate preview count
  // ----------------------------------------------------------

  const previewCount = rows
    ? rows.filter(row => {

        if (
          selectedGroup &&
          row.assigned_group !== selectedGroup
        ) {
          return false
        }


        if (
          dateFrom &&
          (row.created_date || '').slice(0, 10) <
            dateFrom
        ) {
          return false
        }


        if (
          dateTo &&
          (row.created_date || '').slice(0, 10) >
            dateTo
        ) {
          return false
        }


        return true
      }).length

    : 0


  // ----------------------------------------------------------
  // Import filtered tickets
  // ----------------------------------------------------------

  function handleImport() {

    if (!rows) {
      return
    }


    const filtered = rows.filter(row => {

      if (
        selectedGroup &&
        row.assigned_group !== selectedGroup
      ) {
        return false
      }


      if (
        dateFrom &&
        (row.created_date || '').slice(0, 10) <
          dateFrom
      ) {
        return false
      }


      if (
        dateTo &&
        (row.created_date || '').slice(0, 10) >
          dateTo
      ) {
        return false
      }


      return true
    })


    // Need at least 2 tickets

    if (filtered.length < 2) {
      return
    }


    const file = new File(
      [toCSV(filtered)],
      'servicenow_import.csv',
      {
        type: 'text/csv',
      }
    )


    onImport(file)
  }


  // ----------------------------------------------------------
  // Error state — graceful fallback
  // ----------------------------------------------------------

  if (loadErr) {

    return (
      <div
        style={{
          fontSize: 12,
          color: 'var(--text2)',
          marginBottom: 16,
          lineHeight: 1.5,
        }}
      >
        ServiceNow sample data is not loaded.
        <br />
        <span style={{ fontSize: 11, color: 'var(--text3)' }}>
          Please use <strong>Upload CSV</strong> to analyze your tickets.
        </span>
      </div>
    )
  }


  // ----------------------------------------------------------
  // UI
  // ----------------------------------------------------------

  return (
    <>
      {/* Date Range */}

      <div
        style={{
          marginBottom: 12,
        }}
      >

        <div style={filterLabel}>
          <Calendar size={12} />
          Select Date Range
        </div>


        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 8,
          }}
        >

          <input
            type="date"
            value={dateFrom}
            min={dateMin}
            max={dateMax}
            onChange={event => {
              setDateFrom(event.target.value)
            }}
            style={inputStyle}
          />


          <input
            type="date"
            value={dateTo}
            min={dateMin}
            max={dateMax}
            onChange={event => {
              setDateTo(event.target.value)
            }}
            style={inputStyle}
          />

        </div>

      </div>


      {/* Assignment Group */}

      <div
        style={{
          marginBottom: 20,
        }}
      >

        <div style={filterLabel}>
          <Users size={12} />
          Select Assignment Group
        </div>


        <select
          value={selectedGroup}
          onChange={event => {
            setSelectedGroup(event.target.value)
          }}
          style={inputStyle}
        >

          <option value="">
            All Groups
          </option>

          {groups.map(group => (
            <option
              key={group}
              value={group}
            >
              {group}
            </option>
          ))}

        </select>

      </div>


      {/* Preview Count */}

      {rows && (
        <div
          style={{
            fontSize: 11,
            color: 'var(--text2)',
            marginBottom: 12,
          }}
        >

          <strong
            style={{
              color:
                previewCount < 2
                  ? 'var(--red)'
                  : 'var(--accent)',
            }}
          >
            {previewCount}
          </strong>

          {' '}tickets match

        </div>
      )}


      {/* Import Button */}

      <button
        onClick={handleImport}
        disabled={
          processing ||
          previewCount < 2
        }
        style={primaryBtn('var(--purple)')}
      >
        {processing
          ? 'Processing...'
          : 'Import Tickets'}
      </button>

    </>
  )
}


// ============================================================
// SHARED STYLES
// ============================================================

const card = {
  background: 'var(--surface)',
  borderRadius: 18,
  padding: '32px 28px',
  width: 300,
  boxShadow: 'var(--shadow)',
  border: '1px solid var(--border)',
  display: 'flex',
  flexDirection: 'column',
}


const iconBox = bg => ({
  width: 36,
  height: 36,
  borderRadius: 10,
  background: bg,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexShrink: 0,
})


const primaryBtn = bg => ({
  width: '100%',
  padding: '11px',
  borderRadius: 10,
  background: bg,
  border: 'none',
  color: '#fff',
  fontWeight: 700,
  fontSize: 13,
  cursor: 'pointer',
  fontFamily: 'inherit',
  transition: 'opacity 0.15s',
  marginTop: 'auto',
})


const filterLabel = {
  display: 'flex',
  alignItems: 'center',
  gap: 5,
  fontSize: 11,
  fontWeight: 600,
  color: 'var(--text2)',
  marginBottom: 6,
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
}


const inputStyle = {
  width: '100%',
  padding: '9px 10px',
  borderRadius: 8,
  border: '1px solid var(--border)',
  background: 'var(--surface2)',
  color: 'var(--text)',
  fontSize: 12,
  fontFamily: 'inherit',
  outline: 'none',
  boxSizing: 'border-box',
}