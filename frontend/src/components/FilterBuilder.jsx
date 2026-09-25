import React, { useState } from 'react';
import { X, Plus, Play, Trash2, ListFilter } from 'lucide-react';
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
  date: ['is', 'before', 'after', 'on or before', 'on or after', 'is empty', 'is not empty'],
  boolean: ['is true', 'is false', 'is empty', 'is not empty'],
};

// Component for a single condition row
function ConditionRow({ condition, onChange, onRemove, ciList, groupList }) {
  const fieldDef = FIELD_DEFS[condition.field] || { type: 'string' };
  const operators = OPERATORS[fieldDef.type] || OPERATORS.string;

  const handleFieldChange = (e) => {
    const newField = e.target.value;
    const newDef = FIELD_DEFS[newField];
    const newOps = OPERATORS[newDef?.type || 'string'];
    // Reset operator if invalid
    let newOp = condition.operator;
    if (!newOps.includes(newOp)) newOp = newOps[0];
    
    onChange({ ...condition, field: newField, operator: newOp, value: '' });
  };

  const needsValue = !['is empty', 'is not empty', 'is true', 'is false'].includes(condition.operator);
  const isMulti = ['is one of', 'is not one of'].includes(condition.operator);

  let valuesList = [];
  if (fieldDef.type === 'choice') valuesList = fieldDef.values;
  if (fieldDef.type === 'dynamic_choice' && fieldDef.source === 'ciList') valuesList = ciList.map(c => c.ci_name);
  if (fieldDef.type === 'dynamic_choice' && fieldDef.source === 'groupList') valuesList = groupList.map(g => g.group_name);

  return (
    <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 8, flexWrap: 'wrap' }}>
      <select value={condition.field} onChange={handleFieldChange} style={{ minWidth: 180 }}>
        {Object.entries(FIELD_DEFS).map(([k, v]) => (
          <option key={k} value={k}>{v.label}</option>
        ))}
      </select>
      
      <select value={condition.operator} onChange={(e) => onChange({ ...condition, operator: e.target.value })} style={{ minWidth: 140 }}>
        {operators.map(op => <option key={op} value={op}>{op}</option>)}
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
            <input 
              type="date" 
              value={condition.value || ''} 
              onChange={e => onChange({ ...condition, value: e.target.value })} 
              style={{ flex: 1, minWidth: 150 }} 
            />
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

      <button onClick={onRemove} className="btn-ghost" style={{ padding: '8px', color: 'var(--red)' }} title="Remove condition">
        <X size={16} />
      </button>
    </div>
  );
}

// Component for a logical group (AND/OR)
function GroupNode({ group, onChange, onRemove, level = 0, ciList, groupList }) {
  const updateCondition = (index, newCond) => {
    const newConditions = [...group.conditions];
    newConditions[index] = newCond;
    onChange({ ...group, conditions: newConditions });
  };

  const removeCondition = (index) => {
    const newConditions = group.conditions.filter((_, i) => i !== index);
    onChange({ ...group, conditions: newConditions });
  };

  const addCondition = (logic) => {
    // If the group matches the requested logic, just append
    if (group.logic === logic) {
      onChange({ ...group, conditions: [...group.conditions, { field: 'three_r_category', operator: 'is', value: '' }] });
    } else {
      // If adding AND to an OR group (or vice versa), create a nested group if not top level, 
      // or just change logic if only 1 item
      if (group.conditions.length <= 1) {
        onChange({ logic, conditions: [...group.conditions, { field: 'three_r_category', operator: 'is', value: '' }] });
      } else {
        onChange({ ...group, conditions: [...group.conditions, { logic, conditions: [{ field: 'three_r_category', operator: 'is', value: '' }] }] });
      }
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
      borderLeft: `2px solid ${group.logic === 'AND' ? 'var(--accent)' : 'var(--amber)'}`,
      paddingLeft: 16,
      marginLeft: level > 0 ? 12 : 0,
      marginBottom: 16,
      position: 'relative'
    }}>
      {level > 0 && (
        <button 
          onClick={onRemove} 
          className="btn-ghost" 
          style={{ position: 'absolute', top: -10, right: 0, padding: 4, color: 'var(--text2)' }}
        >
          <X size={14} /> Remove Group
        </button>
      )}

      {group.conditions.map((cond, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'flex-start' }}>
          {i > 0 && (
            <div style={{ 
              width: 40, 
              paddingTop: 8,
              fontSize: 12, 
              fontWeight: 600, 
              color: group.logic === 'AND' ? 'var(--accent)' : 'var(--amber)' 
            }}>
              {group.logic}
            </div>
          )}
          {i === 0 && group.conditions.length > 1 && (
            <div style={{ width: 40 }} />
          )}
          <div style={{ flex: 1 }}>
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
                ciList={ciList}
                groupList={groupList}
              />
            )}
          </div>
        </div>
      ))}

      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
        <button onClick={() => addCondition('AND')} className="btn-ghost" style={{ fontSize: 12, padding: '4px 10px' }}>
          <Plus size={14} /> AND
        </button>
        <button onClick={() => addCondition('OR')} className="btn-ghost" style={{ fontSize: 12, padding: '4px 10px' }}>
          <Plus size={14} /> OR
        </button>
        <button onClick={addNestedGroup} className="btn-ghost" style={{ fontSize: 12, padding: '4px 10px' }}>
          <Plus size={14} /> Add Group
        </button>
      </div>
    </div>
  );
}

export default function FilterBuilder({ ast, onChange, onRun, onClear, ciList, groupList }) {
  const [isOpen, setIsOpen] = useState(false);

  // Initialize a default AST if null
  const activeAst = ast || { logic: 'AND', conditions: [] };

  if (!isOpen) {
    return (
      <Card style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 16 }}>
        <ListFilter size={20} color="var(--accent)" />
        <div style={{ flex: 1, fontSize: 13, color: 'var(--text2)' }}>
          {activeAst.conditions.length === 0 ? "No advanced filters applied." : `${activeAst.conditions.length} top-level conditions applied.`}
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

      <div style={{ background: 'var(--bg)', padding: 16, borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
        {activeAst.conditions.length === 0 ? (
          <div style={{ padding: '20px 0', textAlign: 'center', color: 'var(--text2)', fontSize: 13 }}>
            No conditions. Click below to add one.
          </div>
        ) : (
          <GroupNode 
            group={activeAst} 
            onChange={onChange} 
            ciList={ciList}
            groupList={groupList}
          />
        )}
        
        {activeAst.conditions.length === 0 && (
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: 12 }}>
            <button 
              onClick={() => onChange({ logic: 'AND', conditions: [{ field: 'three_r_category', operator: 'is', value: '' }] })}
              className="btn-ghost"
            >
              <Plus size={16} /> Add Condition
            </button>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 16 }}>
        <button onClick={onClear} className="btn-ghost" style={{ color: 'var(--red)', borderColor: 'transparent' }}>
          <Trash2 size={16} /> Clear All
        </button>
        <button onClick={onRun} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Play size={16} /> Run Filter
        </button>
      </div>
    </Card>
  );
}
