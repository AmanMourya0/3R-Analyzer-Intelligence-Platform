# 3R Analyzer Filter Builder

The Advanced Filter Builder provides a ServiceNow-inspired interface for constructing complex filtering criteria.

## Architecture

The filter builder creates an Abstract Syntax Tree (AST) that is converted into SQLAlchemy query filters in the backend, while remaining cleanly serialized into the frontend URL for easy sharing and persistence.

The AST follows a consistent nested structure:
```json
{
  "logic": "AND",
  "conditions": [
    {
      "field": "priority",
      "operator": "is",
      "value": "P1"
    }
  ]
}
```

### Condition Row Model

Each visual condition row explicitly controls its own branching:
```text
[Field] [Operator] [Value]      [AND] [OR] [×]
```

When you click `AND` or `OR` next to a condition, the builder explicitly inserts the requested logical sibling condition at the exact same logical level.

### Explicit Group Behavior

If the parent logic is `AND` and the user clicks `OR` on a specific condition, the builder automatically constructs a new nested AST group (`OR`) and wraps the target condition, ensuring deterministic resolution without relying on implicit SQL operator precedence.

For example, starting with:
```text
All of these conditions must be met

[Priority] [is] [P1]             [AND][OR][×]
```

If the user clicks `OR` on that row, the UI produces:
```text
All of these conditions must be met

┌──────────────────────────────────────────────┐
│ [Priority] [is] [P1]             [AND][OR][×]│
│ OR                                            │
│ [Priority] [is] [P2]             [AND][OR][×]│
└──────────────────────────────────────────────┘
```

Resulting in the AST:
```json
{
  "logic": "AND",
  "conditions": [
    {
      "logic": "OR",
      "conditions": [
        { "field": "priority", "operator": "is", "value": "P1" },
        { "field": "priority", "operator": "is", "value": "P2" }
      ]
    }
  ]
}
```

This prevents the ambiguous scenario of:
```text
A AND B OR C
```

## Backend Compatibility

The frontend Filter Builder generates the AST strictly aligned with the backend's `FilterGroup` and `FilterCondition` Pydantic schemas. 

* The field names match the `query_builder.py` allowlist (e.g. `three_r_category`, `assigned_group`).
* The UI operators map seamlessly to the supported SQLAlchemy directives (`eq`, `in`, `like`, `isnull`, etc.).
* Invalid conditions (missing values, mismatched operators) are rejected on the frontend to prevent backend `422 Unprocessable Entity` errors.

## URL Persistence

The top-level `activeAst` JSON is serialized into a URI-encoded query string (`?filter=...`). Upon page load, this structure is deserialized and instantly restores the UI group nesting seamlessly. 

## Date & Date-Range Filtering

The filter builder fully supports ServiceNow-style date and datetime filtering with the following operators:
* `on`: Exact calendar day.
* `not_on`: Excludes exact calendar day.
* `before`: Strictly before the given date.
* `at_or_before`: Up to and including the calendar day.
* `after`: Strictly after the given date.
* `at_or_after`: On or after the calendar day.
* `between`: A range bounded by a start and end calendar day.
* `is_empty`: SQL NULL check.
* `is_not_empty`: SQL NOT NULL check.

### The `between` Operator

When the user selects the `between` operator, the filter builder renders two inline date pickers. The range is represented as a **single condition** in the AST to preserve semantic clarity and URL persistence:

```text
Resolved Date between 01/09/2026 and 30/09/2026
```

AST Representation:
```json
{
  "field": "resolved_date",
  "operator": "between",
  "value": {
    "from": "2026-09-01",
    "to": "2026-09-30"
  }
}
```

### Date vs Datetime Handling
In the backend (`query_builder.py`), date operations intelligently account for `DATETIME` properties using half-open intervals. For example, querying `between 2026-09-01 and 2026-09-30` translates to:
`>= 2026-09-01 00:00:00` AND `< 2026-10-01 00:00:00`
This guarantees incidents that occurred on the afternoon of `2026-09-30` are correctly included.

### Validation
Invalid date ranges (where the start date is after the end date) or incomplete date ranges will fail the frontend `isConditionComplete` validation. The **Run Filter** button is disabled until the criteria are structurally valid.
