import React from 'react';
import { Plus, X, ArrowUpAZ, ArrowDownZA, ArrowDownAz, ArrowUpZa } from 'lucide-react';

const FIELD_DEFS = {
  incident_number: 'Incident Number',
  short_description: 'Short Description',
  three_r_category: '3R Category',
  cluster_name: 'Cluster Name',
  cluster_id: 'Cluster ID',
  semantic_match_cluster_id: 'Semantic Match Cluster ID',
  ci_name: 'CI / Application',
  assigned_group: 'Assignment Group',
  priority: 'Priority',
  state: 'State',
  region: 'Region',
  problem_candidate: 'Problem Candidate',
  three_r_reason: '3R Reason',
  created_date: 'Created Date',
  resolved_date: 'Resolved Date',
};

export default function SortBuilder({ sorts, onChange }) {
  const activeSorts = sorts || [];

  const addSort = () => {
    onChange([...activeSorts, { field: 'created_date', direction: 'DESC' }]);
  };

  const removeSort = (index) => {
    onChange(activeSorts.filter((_, i) => i !== index));
  };

  const updateSort = (index, newSort) => {
    const newSorts = [...activeSorts];
    newSorts[index] = newSort;
    onChange(newSorts);
  };

  if (activeSorts.length === 0) {
    return (
      <div style={{ marginTop: 12 }}>
        <button onClick={addSort} className="btn-ghost" style={{ fontSize: 12, padding: '4px 10px' }}>
          <Plus size={14} /> Add Sort
        </button>
      </div>
    );
  }

  return (
    <div style={{ marginTop: 16 }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text2)', textTransform: 'uppercase', marginBottom: 8, letterSpacing: '0.05em' }}>
        Sort By
      </div>
      {activeSorts.map((sort, index) => (
        <div key={index} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <div style={{ fontSize: 12, color: 'var(--text2)', width: 60 }}>
            {index === 0 ? 'First by' : 'Then by'}
          </div>
          <select 
            value={sort.field} 
            onChange={e => updateSort(index, { ...sort, field: e.target.value })}
            style={{ minWidth: 160 }}
          >
            {Object.entries(FIELD_DEFS).map(([k, label]) => (
              <option key={k} value={k}>{label}</option>
            ))}
          </select>
          <button 
            className="btn-ghost" 
            onClick={() => updateSort(index, { ...sort, direction: sort.direction === 'ASC' ? 'DESC' : 'ASC' })}
            style={{ width: 100, justifyContent: 'center' }}
            title="Toggle sort direction"
          >
            {sort.direction === 'ASC' ? <ArrowUpAZ size={16} /> : <ArrowDownZA size={16} />}
            {sort.direction}
          </button>
          <button onClick={() => removeSort(index)} className="btn-ghost" style={{ padding: 6, color: 'var(--text2)', borderColor: 'transparent' }}>
            <X size={14} />
          </button>
        </div>
      ))}
      <div style={{ marginTop: 8 }}>
        <button onClick={addSort} className="btn-ghost" style={{ fontSize: 12, padding: '4px 10px' }}>
          <Plus size={14} /> Add Sort
        </button>
      </div>
    </div>
  );
}
