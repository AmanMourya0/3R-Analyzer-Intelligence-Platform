# Advanced Filter Builder

The platform features a ServiceNow-style Advanced Filter Builder allowing complex AST (Abstract Syntax Tree) query generation.

## Supported Logic
* Nested Groups: `AND` / `OR`
* Operators: `==`, `!=`, `>`, `<`, `>=`, `<=`, `in`, `not_in`, `contains`, `not_contains`, `starts_with`, `ends_with`, `between`, `is_empty`, `is_not_empty`.

## Abstract Syntax Tree (AST) Example
Filters are serialized as JSON and passed via query parameters to the backend:
```json
{
  "type": "group",
  "logic": "AND",
  "conditions": [
    {
      "type": "condition",
      "field": "priority",
      "operator": "in",
      "value": ["1 - Critical", "2 - High"]
    },
    {
      "type": "group",
      "logic": "OR",
      "conditions": [
        {
          "type": "condition",
          "field": "assignment_group",
          "operator": "==",
          "value": "Database Admins"
        }
      ]
    }
  ]
}
```

## Backend Validation
The backend `QueryBuilder` walks this AST, safely translates it to SQLAlchemy clauses, and enforces the `FIELD_REGISTRY` to prevent SQL injection or invalid column references.
