import React, { useState } from 'react';
import { Download, ChevronDown, FileText, FileSpreadsheet, LayoutDashboard, Loader2 } from 'lucide-react';

export default function ExportMenu({ ast, sorts }) {
  const [isOpen, setIsOpen] = useState(false);
  const [loadingType, setLoadingType] = useState(null);

  const downloadFile = async (url, filename) => {
    try {
      setLoadingType(filename);
      // We manually construct the full query string so we can hit the API endpoint
      const params = new URLSearchParams();
      if (ast) params.append('filter', JSON.stringify(ast));
      if (sorts) params.append('sort', JSON.stringify(sorts));
      
      const queryString = params.toString();
      const finalUrl = `http://127.0.0.1:8000/api${url}${queryString ? `?${queryString}` : ''}`;
      
      const response = await fetch(finalUrl);
      if (!response.ok) throw new Error('Network response was not ok');
      
      const blob = await response.blob();
      const objectUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = objectUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(objectUrl);
    } catch (err) {
      console.error('Download failed', err);
      alert('Export failed. Please check the backend connection.');
    } finally {
      setLoadingType(null);
      setIsOpen(false);
    }
  };

  const handleExport = (type) => {
    const d = new Date().toISOString().split('T')[0];
    if (type === 'tickets') {
      downloadFile('/export/tickets/csv', `3R_Tickets_Export_${d}.csv`);
    } else if (type === 'clusters') {
      downloadFile('/export/clusters/csv', `3R_Cluster_Report_${d}.csv`);
    } else if (type === 'summary') {
      downloadFile('/export/summary/csv', `3R_Summary_Report_${d}.csv`);
    } else if (type === 'executive') {
      downloadFile('/export/executive-report/pdf', `3R_Executive_Report_${d}.pdf`);
    }
  };

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <button 
        onClick={() => setIsOpen(!isOpen)} 
        className="btn-ghost" 
        style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 14px', background: 'var(--surface2)', borderColor: 'var(--border2)' }}
      >
        <Download size={16} />
        Export
        <ChevronDown size={14} />
      </button>

      {isOpen && (
        <>
          <div 
            onClick={() => setIsOpen(false)}
            style={{ position: 'fixed', inset: 0, zIndex: 99 }}
          />
          <div 
            style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              marginTop: 8,
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-sm)',
              boxShadow: 'var(--shadow)',
              zIndex: 100,
              minWidth: 220,
              overflow: 'hidden'
            }}
          >
            <div style={{ padding: '8px 12px', fontSize: 11, fontWeight: 600, color: 'var(--text2)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--border)' }}>
              Data Exports (CSV)
            </div>
            
            <button 
              className="export-menu-btn" 
              onClick={() => handleExport('tickets')}
              disabled={loadingType !== null}
            >
              {loadingType === `3R_Tickets_Export_${new Date().toISOString().split('T')[0]}.csv` ? <Loader2 size={16} className="spin" /> : <FileSpreadsheet size={16} />}
              Filtered Tickets
            </button>
            <button 
              className="export-menu-btn" 
              onClick={() => handleExport('clusters')}
              disabled={loadingType !== null}
            >
              {loadingType === `3R_Cluster_Report_${new Date().toISOString().split('T')[0]}.csv` ? <Loader2 size={16} className="spin" /> : <FileSpreadsheet size={16} />}
              Clusters & Analytics
            </button>
            <button 
              className="export-menu-btn" 
              onClick={() => handleExport('summary')}
              disabled={loadingType !== null}
            >
              {loadingType === `3R_Summary_Report_${new Date().toISOString().split('T')[0]}.csv` ? <Loader2 size={16} className="spin" /> : <LayoutDashboard size={16} />}
              3R Summary Metrics
            </button>
            
            <div style={{ padding: '8px 12px', fontSize: 11, fontWeight: 600, color: 'var(--text2)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--border)', borderTop: '1px solid var(--border)' }}>
              Executive Reports (PDF)
            </div>
            <button 
              className="export-menu-btn" 
              style={{ color: 'var(--text)' }}
              onClick={() => handleExport('executive')}
              disabled={loadingType !== null}
            >
              {loadingType === `3R_Executive_Report_${new Date().toISOString().split('T')[0]}.pdf` ? <Loader2 size={16} className="spin" /> : <FileText size={16} color="var(--purple)" />}
              Leadership Report
            </button>
          </div>
        </>
      )}
      <style>{`
        .export-menu-btn {
          display: flex;
          align-items: center;
          gap: 12px;
          width: 100%;
          padding: 12px 16px;
          background: transparent;
          border: none;
          color: var(--text2);
          font-size: 13px;
          text-align: left;
          cursor: pointer;
          transition: all 0.15s;
        }
        .export-menu-btn:hover:not(:disabled) {
          background: var(--surface2);
          color: var(--text);
        }
        .export-menu-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
