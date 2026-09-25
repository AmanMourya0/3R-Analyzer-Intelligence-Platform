import React from 'react';
import { X, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Badge from './Badge';

export default function TicketDrawer({ ticket, onClose }) {
  const navigate = useNavigate();

  if (!ticket) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const isRunner = ticket.three_r_category === 'RUNNER';
  const isRepeater = ticket.three_r_category === 'REPEATER';
  const isRare = ticket.three_r_category === 'RARE';

  return (
    <div 
      onClick={handleBackdropClick}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        zIndex: 1000,
        display: 'flex',
        justifyContent: 'flex-end',
        backdropFilter: 'blur(2px)'
      }}
    >
      <div 
        className="fade-up"
        style={{
          width: 500,
          maxWidth: '100%',
          backgroundColor: 'var(--bg)',
          borderLeft: '1px solid var(--border)',
          height: '100%',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '-4px 0 24px rgba(0,0,0,0.5)'
        }}
      >
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, background: 'var(--bg)', zIndex: 10 }}>
          <div>
            <div style={{ fontSize: 13, color: 'var(--text2)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Incident Detail</div>
            <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>{ticket.ticket_id}</div>
          </div>
          <button onClick={onClose} className="btn-ghost" style={{ padding: 8, borderColor: 'transparent' }}>
            <X size={20} />
          </button>
        </div>

        <div style={{ padding: '24px' }}>
          <div style={{ marginBottom: 32 }}>
            <div style={{ fontSize: 16, fontWeight: 500 }}>{ticket.short_description}</div>
            {ticket.description && (
              <div style={{ fontSize: 13, color: 'var(--text2)', marginTop: 12, padding: 12, background: 'var(--surface2)', borderRadius: 'var(--radius-sm)', whiteSpace: 'pre-wrap' }}>
                {ticket.description}
              </div>
            )}
          </div>

          {/* 3R Intelligence Section */}
          <div style={{ marginBottom: 32, padding: 20, background: 'linear-gradient(135deg, rgba(15,98,254,0.05), rgba(124,58,237,0.05))', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
            <div style={{ fontSize: 14, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <span style={{ fontSize: 18 }}>🧠</span> 3R Intelligence
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '12px 16px', fontSize: 13 }}>
              <div style={{ color: 'var(--text2)' }}>Classification</div>
              <div>
                <Badge color={isRunner ? 'var(--red)' : isRepeater ? 'var(--amber)' : isRare ? 'var(--purple)' : 'var(--text2)'}>
                  {ticket.three_r_category || 'UNCLASSIFIED'}
                </Badge>
              </div>

              <div style={{ color: 'var(--text2)' }}>Reason</div>
              <div style={{ fontWeight: 500, color: ticket.three_r_reason ? 'var(--text)' : 'var(--text2)' }}>
                {ticket.three_r_reason || 'Classification reason not available'}
              </div>

              <div style={{ color: 'var(--text2)' }}>Problem Candidate</div>
              <div>
                {ticket.problem_candidate ? <Badge color="var(--accent)">Yes</Badge> : <span style={{ color: 'var(--text2)' }}>No</span>}
              </div>

              <div style={{ color: 'var(--text2)' }}>Cluster ID</div>
              <div>{ticket.cluster_id !== -1 ? ticket.cluster_id : <span style={{ color: 'var(--text2)' }}>Noise / None</span>}</div>

              <div style={{ color: 'var(--text2)' }}>Cluster Name</div>
              <div>{ticket.cluster_name}</div>
              
              {ticket.semantic_match_cluster_id && (
                <>
                  <div style={{ color: 'var(--text2)' }}>Semantic Match</div>
                  <div>Cluster {ticket.semantic_match_cluster_id}</div>
                </>
              )}
            </div>

            {ticket.cluster_id !== -1 && ticket.cluster_id != null && (
              <div style={{ marginTop: 20 }}>
                <button 
                  className="btn-primary" 
                  style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 8 }}
                  onClick={() => navigate(`/clusters?cluster_id=${ticket.cluster_id}`)}
                >
                  <ExternalLink size={16} /> View Cluster Intelligence
                </button>
              </div>
            )}
          </div>

          {/* Properties Section */}
          <div style={{ marginBottom: 24 }}>
            <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 16, borderBottom: '1px solid var(--border)', paddingBottom: 8 }}>
              Properties
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '12px 16px', fontSize: 13 }}>
              <div style={{ color: 'var(--text2)' }}>Priority</div>
              <div>{ticket.priority || '—'}</div>
              
              <div style={{ color: 'var(--text2)' }}>State</div>
              <div>{ticket.status || '—'}</div>
              
              <div style={{ color: 'var(--text2)' }}>CI / App</div>
              <div>{ticket.ci_name || '—'}</div>
              
              <div style={{ color: 'var(--text2)' }}>Assignment Group</div>
              <div>{ticket.assigned_group || '—'}</div>
              
              <div style={{ color: 'var(--text2)' }}>Created Date</div>
              <div>{ticket.created_date || '—'}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
