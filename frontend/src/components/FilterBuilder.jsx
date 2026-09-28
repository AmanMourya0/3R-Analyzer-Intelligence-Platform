import React, { useState } from 'react';
import { X, Plus, Play, Trash2, ListFilter, AlertCircle } from 'lucide-react';
import Card from './Card';

const FIELD_DEFS = {
  incident_number: { label: 'Incident Number', type: 'string' },
  short_description: { label: 'Short Description', type: 'string' },
  description: { label: 'Description', type: 'string' },
  three_r_category: { label: '3R Category', type: 'choice', values: ['RUNNER', 'REPEATER', 'RARE'] },
  cluster_name: { label: 'Cluster Name', type: 'string' },
  cluster_id: { label: 'Cluster ID', type: 'numeric' },
  semantic_match_cluster_id: { label: 'Semantic Match Cluster ID', type: 'numeric' },
  ci_name: { label: 'CI / Application', type: 'dynamic_choice', source: 'ciList' },
  assigned_group: { label: 'Assignment Group', type: 'dynamic_choice', source: 'groupList' },
  priority: { label: 'Priority', type: 'choice', values: ['Critical', 'High', 'Medium', 'Low', 'P1', 'P2', 'P3', 'P4'] },
  state: { label: 'State', type: 'choice', values: ['New', 'In Progress', 'On Hold', 'Resolved', 'Closed', 'Canceled'] },
  region: { label: 'Region', type: 'string' },
  problem_candidate: { label: 'Problem Candidate', type: 'boolean' },
  three_r_reason: { label: '3R Reason', type: 'string' },
  created_date: { label: 'Created Date', type: 'date' },
  resolved_date: { label: 'Resolved Date', type: 'date' },
};

const OPERATORS = {
  string: ['is', 'is not', 'contains', 'does not contain', 'starts with', 'ends with', 'is empty', 'is not empty'],
  choice: ['is', 'is not', 'is one of', 'is not one of', 'is empty', 'is not empty'],
  dynamic_choice: ['is', 'is not', 'is one of', 'is not one of', 'is empty', 'is not empty'],
  numeric: ['is', 'is not', 'greater than', 'greater than or equal', 'less than', 'less than or equal', 'is empty', 'is not empty'],
  date: ['on', 'not_on', 'before', 'at_or_before', 'after', 'at_or_after', 'between', 'is empty', 'is not empty'],
  boolean: ['is true', 'is false', 'is empty', 'is not empty'],
};

// Check if a condition is complete
const isConditionComplete = (cond) => {
  if (cond.conditions) {
    return cond.conditions.every(isConditionComplete);
  }
  const needsValue = !['is empty', 'is not empty', 'is true', 'is false'].includes(cond.operator);
  if (needsValue) {
    if (cond.operator === 'between') {
      return cond.value && cond.value.from && cond.value.to && cond.value.from <= cond.value.to;
    }
    if (Array.isArray(cond.value)) return cond.value.length > 0;
    return cond.value !== '' && cond.value !== null && cond.value !== undefined;
  }
  return true;
};

function ConditionRow({ condition, onChange, onRemove, onAddSibling, ciList, groupList }) {
  const fieldDef = FIELD_DEFS[condition.field] || { type: 'string' };
  const operators = OPERATORS[fieldDef.type] || OPERATORS.string;

  const handleFieldChange = (e) => {
    const newField = e.target.value;
    const newDef = FIELD_DEFS[newField];
    const newOps = OPERATORS[newDef?.type || 'string'];
    let newOp = condition.operator;
    if (!newOps.includes(newOp)) newOp = newOps[0];
    onChange({ ...condition, field: newField, operator: newOp, value: '' });
  };

  const needsValue = !['is empty', 'is not empty', 'is true', 'is false'].includes(condition.operator);
  const isMulti = ['is one of', 'is not one of'].includes(condition.operator);
  const isComplete = isConditionComplete(condition);

  let valuesList = [];
  if (fieldDef.type === 'choice') valuesList = fieldDef.values;
  if (fieldDef.type === 'dynamic_choice' && fieldDef.source === 'ciList') valuesList = ciList.map(c => c.ci_name);
  if (fieldDef.type === 'dynamic_choice' && fieldDef.source === 'groupList') valuesList = groupList.map(g => g.group_name);

  return (
    <div style={{ 
      display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap', 
      padding: '4px 0',
      border: !isComplete ? '1px dashed var(--amber)' : '1px solid transparent',
      borderRadius: '4px'
    }}>
      <select value={condition.field} onChange={handleFieldChange} style={{ minWidth: 180 }}>
        {Object.entries(FIELD_DEFS).map(([k, v]) => (
          <option key={k} value={k}>{v.label}</option>
        ))}
      </select>
      
      <select 
        value={condition.operator} 
        onChange={(e) => {
          const newOp = e.target.value;
          let newVal = condition.value;
          if (newOp === 'between' && (typeof newVal !== 'object' || newVal === null || Array.isArray(newVal))) {
            newVal = { from: '', to: '' };
          } else if (condition.operator === 'between' && newOp !== 'between') {
            newVal = '';
          }
          onChange({ ...condition, operator: newOp, value: newVal });
        }} 
        style={{ minWidth: 140 }}
      >
        {operators.map(op => <option key={op} value={op}>{op.replace(/_/g, ' ')}</option>)}
      </select>

      {needsValue && (
        <>
          {['choice', 'dynamic_choice'].includes(fieldDef.type) ? (
            isMulti ? (
              <input 
                type="text" 
                placeholder="Comma separated values" 
                value={Array.isArray(condition.value) ? condition.value.join(', ') : condition.value}
                onChange={e => onChange({ ...condition, value: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                style={{ flex: 1, minWidth: 200 }}
              />
            ) : (
              <select 
                value={condition.value} 
                onChange={e => onChange({ ...condition, value: e.target.value })}
                style={{ flex: 1, minWidth: 200 }}
              >
                <option value="">-- Select --</option>
                {valuesList.map(v => <option key={v} value={v}>{v}</option>)}
              </select>
            )
          ) : fieldDef.type === 'date' ? (
            condition.operator === 'between' ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <input 
                  type="date" 
                  value={condition.value?.from || ''} 
                  onChange={e => onChange({ ...condition, value: { ...condition.value, from: e.target.value } })} 
                  style={{ width: 150 }} 
                />
                <span style={{ fontSize: 13, color: 'var(--text2)' }}>and</span>
                <input 
                  type="date" 
                  value={condition.value?.to || ''} 
                  onChange={e => onChange({ ...condition, value: { ...condition.value, to: e.target.value } })} 
                  style={{ width: 150 }} 
                />
              </div>
            ) : (
              <input 
                type="date" 
                value={condition.value || ''} 
                onChange={e => onChange({ ...condition, value: e.target.value })} 
                style={{ flex: 1, minWidth: 150 }} 
              />
            )
          ) : fieldDef.type === 'numeric' ? (
            <input 
              type="number" 
              value={condition.value || ''} 
              onChange={e => onChange({ ...condition, value: e.target.value === '' ? '' : Number(e.target.value) })} 
              style={{ flex: 1, minWidth: 150 }} 
            />
          ) : (
            <input 
              type="text" 
              placeholder="Value"
              value={condition.value || ''} 
              onChange={e => onChange({ ...condition, value: e.target.value })} 
              style={{ flex: 1, minWidth: 200 }} 
            />
          )}
        </>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginLeft: 'auto' }}>
        <button onClick={() => onAddSibling('AND')} className="btn-ghost" style={{ padding: '4px 8px', fontSize: 12, border: '1px solid var(--border)', background: 'var(--bg)' }}>AND</button>
        <button onClick={() => onAddSibling('OR')} className="btn-ghost" style={{ padding: '4px 8px', fontSize: 12, border: '1px solid var(--border)', background: 'var(--bg)' }}>OR</button>
        <button onClick={onRemove} className="btn-ghost" style={{ padding: '4px 6px', color: 'var(--red)', border: '1px solid transparent' }} title="Remove condition"><X size={16} /></button>
      </div>
    </div>
  );
}

function GroupNode({ group, onChange, onRemove, level = 0, ciList, groupList }) {
  const isRoot = level === 0;

  const updateCondition = (index, newCond) => {
    const newConditions = [...group.conditions];
    newConditions[index] = newCond;
    onChange({ ...group, conditions: newConditions });
  };

  const removeCondition = (index) => {
    const newConditions = group.conditions.filter((_, i) => i !== index);
    if (newConditions.length === 0) {
      if (isRoot) {
        onChange({ ...group, conditions: [] });
      } else {
        onRemove();
      }
    } else if (newConditions.length === 1 && !isRoot) {
      // Auto-unwrap if only 1 child remains in a nested group
      onChange(newConditions[0]);
    } else {
      onChange({ ...group, conditions: newConditions });
    }
  };

  const addSiblingCondition = (index, logic) => {
    const newCond = { field: 'priority', operator: 'is', value: '' };
    
    // If the group has 1 or fewer conditions, just adopt the requested logic
    if (group.conditions.length <= 1) {
      onChange({ logic, conditions: [...group.conditions, newCond] });
    } else if (group.logic === logic) {
      // Same logic, insert after index
      const newConditions = [...group.conditions];
      newConditions.splice(index + 1, 0, newCond);
      onChange({ ...group, conditions: newConditions });
    } else {
      // Opposite logic, explicitly nest the current condition and the new one
      const targetCond = group.conditions[index];
      const newGroup = { logic, conditions: [targetCond, newCond] };
      const newConditions = [...group.conditions];
      newConditions[index] = newGroup;
      onChange({ ...group, conditions: newConditions });
    }
  };

  const addNestedGroup = () => {
    onChange({
      ...group,
      conditions: [...group.conditions, { logic: group.logic === 'AND' ? 'OR' : 'AND', conditions: [{ field: 'three_r_category', operator: 'is', value: '' }] }]
    });
  };

  return (
    <div style={{
      border: isRoot ? 'none' : '1px solid var(--border)',
      borderLeft: isRoot ? 'none' : `3px solid ${group.logic === 'AND' ? 'var(--accent)' : 'var(--amber)'}`,
      padding: isRoot ? 0 : 16,
      borderRadius: isRoot ? 0 : 6,
      background: isRoot ? 'transparent' : 'var(--bg-elevated)',
      marginBottom: isRoot ? 0 : 12,
      position: 'relative'
    }}>
      {isRoot && group.conditions.length > 0 && (
        <div style={{ marginBottom: 12, fontSize: 13, display: 'flex', alignItems: 'center', gap: 8 }}>
          <select 
            value={group.logic} 
            onChange={e => onChange({ ...group, logic: e.target.value })}
            style={{ 
              padding: '6px 10px', 
              fontSize: 13, 
              border: '1px solid var(--border)', 
              borderRadius: '4px',
              background: 'var(--bg)', 
              fontWeight: 600, 
              cursor: 'pointer', 
              color: 'var(--text)'
            }}
          >
            <option value="AND">All of these conditions must be met</option>
            <option value="OR">Any of these conditions may be met</option>
          </select>
        </div>
      )}

      {!isRoot && (
        <button 
          onClick={onRemove} 
          className="btn-ghost" 
          style={{ position: 'absolute', top: -12, right: -12, padding: 4, background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '50%', color: 'var(--text2)' }}
          title="Remove Group"
        >
          <X size={14} />
        </button>
      )}

      {group.conditions.map((cond, i) => (
        <React.Fragment key={i}>
          {i > 0 && (
            <div style={{ 
              padding: '6px 0',
              fontSize: 12, 
              fontWeight: 600, 
              color: group.logic === 'AND' ? 'var(--accent)' : 'var(--amber)',
              width: '40px'
            }}>
              {group.logic}
            </div>
          )}
          <div>
            {cond.conditions ? (
              <GroupNode 
                group={cond} 
                onChange={(c) => updateCondition(i, c)} 
                onRemove={() => removeCondition(i)}
                level={level + 1}
                ciList={ciList}
                groupList={groupList}
              />
            ) : (
              <ConditionRow 
                condition={cond} 
                onChange={(c) => updateCondition(i, c)}
                onRemove={() => removeCondition(i)}
                onAddSibling={(logic) => addSiblingCondition(i, logic)}
                ciList={ciList}
                groupList={groupList}
              />
            )}
          </div>
        </React.Fragment>
      ))}

      {isRoot && group.conditions.length > 0 && (
        <div style={{ display: 'flex', gap: 8, marginTop: 16, paddingTop: 16, borderTop: '1px dashed var(--border)' }}>
          <button onClick={addNestedGroup} className="btn-ghost" style={{ fontSize: 13, padding: '4px 10px' }}>
            <Plus size={14} /> Add Advanced Group
          </button>
        </div>
      )}
    </div>
  );
}

// Generate human readable string for AST
function summarizeAst(ast) {
  if (!ast || !ast.conditions || ast.conditions.length === 0) return "No advanced filters applied.";
  
  const buildString = (node) => {
    if (node.conditions) {
      const parts = node.conditions.map(buildString).filter(Boolean);
      if (parts.length === 0) return "";
      if (parts.length === 1) return parts[0];
      const joined = parts.join(` ${node.logic} `);
      // Only wrap in parens if it's not the root or if it's a nested expression
      return `(${joined})`;
    }
    
    // It's a leaf condition
    const fieldLabel = FIELD_DEFS[node.field]?.label || node.field;
    let opLabel = node.operator.replace(/_/g, ' ');

    const formatDt = (d) => {
      if (!d) return '...';
      const parts = String(d).split('-');
      if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`;
      return String(d);
    };

    if (node.operator === 'between') {
      const from = node.value?.from;
      const to = node.value?.to;
      return `${fieldLabel} between ${formatDt(from)} and ${formatDt(to)}`;
    }

    let valStr = node.value;
    if (Array.isArray(valStr)) valStr = valStr.join(', ');
    if (FIELD_DEFS[node.field]?.type === 'date' && valStr) {
      valStr = formatDt(valStr);
    }
    return `${fieldLabel} ${opLabel} ${valStr !== undefined && valStr !== '' ? valStr : '...'}`;
  };

  const parts = ast.conditions.map(buildString).filter(Boolean);
  if (parts.length === 0) return "No complete conditions.";
  if (parts.length === 1) return parts[0];
  return parts.join(` ${ast.logic} `);
}

export default function FilterBuilder({ ast, onChange, onRun, onClear, ciList, groupList }) {
  const [isOpen, setIsOpen] = useState(false);

  // Initialize a default AST if null
  const activeAst = ast || { logic: 'AND', conditions: [] };
  
  // Validation check
  const isValid = activeAst.conditions.length === 0 || activeAst.conditions.every(isConditionComplete);

  if (!isOpen) {
    return (
      <Card style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 16 }}>
        <ListFilter size={20} color="var(--accent)" />
        <div style={{ flex: 1, fontSize: 13, color: 'var(--text)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {summarizeAst(activeAst)}
        </div>
        <button onClick={() => setIsOpen(true)} className="btn-ghost">
          Edit Filters
        </button>
      </Card>
    );
  }

  return (
    <Card style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, paddingBottom: 12, borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600 }}>
          <ListFilter size={18} color="var(--accent)" /> Advanced Filter Builder
        </div>
        <button onClick={() => setIsOpen(false)} className="btn-ghost" style={{ padding: '4px' }}>
          <X size={18} />
        </button>
      </div>

      <div style={{ background: 'var(--bg)', padding: '20px 24px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
        {activeAst.conditions.length === 0 ? (
          <div style={{ padding: '20px 0', textAlign: 'center', color: 'var(--text2)', fontSize: 13 }}>
            No conditions defined.
            <div style={{ marginTop: 12 }}>
              <button 
                onClick={() => onChange({ logic: 'AND', conditions: [{ field: 'three_r_category', operator: 'is', value: '' }] })}
                className="btn-primary"
              >
                <Plus size={16} /> Add Condition
              </button>
            </div>
          </div>
        ) : (
          <GroupNode 
            group={activeAst} 
            onChange={onChange} 
            ciList={ciList}
            groupList={groupList}
          />
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 16, alignItems: 'center' }}>
        <button onClick={onClear} className="btn-ghost" style={{ color: 'var(--red)', borderColor: 'transparent' }}>
          <Trash2 size={16} /> Clear All
        </button>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {!isValid && (
            <span style={{ fontSize: 12, color: 'var(--amber)', display: 'flex', alignItems: 'center', gap: 4 }}>
              <AlertCircle size={14} /> Missing values
            </span>
          )}
          <button 
            onClick={onRun} 
            className="btn-primary" 
            style={{ display: 'flex', alignItems: 'center', gap: 8, opacity: isValid ? 1 : 0.5, cursor: isValid ? 'pointer' : 'not-allowed' }}
            disabled={!isValid}
          >
            <Play size={16} /> Run Filter
          </button>
        </div>
      </div>
    </Card>
  );
}
