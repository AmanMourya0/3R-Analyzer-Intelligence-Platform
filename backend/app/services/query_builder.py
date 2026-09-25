import json
from typing import Any, List, Optional
from sqlalchemy import or_, and_, asc, desc
from sqlalchemy.orm import Query

from app.database.incident_model import Incident
from app.database.cluster_model import Cluster
from app.database.recurrence_model import Recurrence
from app.schemas.filter_ast import FilterCondition, FilterGroup, SortRule


# Define the field registry
# Maps logical field names to SQLAlchemy columns
FIELD_REGISTRY = {
    "incident_number": Incident.incident_number,
    "short_description": Incident.short_description,
    "description": Incident.description,
    "three_r_category": Incident.three_r_category,
    "cluster_id": Incident.cluster_id,
    "cluster_name": Cluster.cluster_name,
    "semantic_match_cluster_id": Incident.semantic_match_cluster_id,
    "ci_name": Incident.configuration_item,
    "assigned_group": Incident.assignment_group,
    "priority": Incident.priority,
    "state": Incident.state,
    "region": Incident.region,
    "problem_candidate": Recurrence.problem_candidate,
    "three_r_reason": Cluster.three_r_reason,
    "created_date": Incident.created_date,
    "resolved_date": Incident.resolved_date,
}


def build_filter_expression(ast: FilterGroup):
    """
    Recursively builds a SQLAlchemy filter expression from the AST.
    """
    expressions = []
    for item in ast.conditions:
        if isinstance(item, FilterGroup):
            expr = build_filter_expression(item)
            if expr is not None:
                expressions.append(expr)
        else:
            condition = item
            if condition.field not in FIELD_REGISTRY:
                raise ValueError(f"Invalid field: {condition.field}")

            column = FIELD_REGISTRY[condition.field]
            op = condition.operator
            val = condition.value

            # Build operator logic
            if op == "eq" or op == "is":
                expr = column == val
            elif op == "neq" or op == "is not":
                expr = column != val
            elif op == "in" or op == "is one of":
                if not isinstance(val, list):
                    raise ValueError(f"Operator '{op}' requires a list value.")
                expr = column.in_(val)
            elif op == "not_in" or op == "is not one of":
                if not isinstance(val, list):
                    raise ValueError(f"Operator '{op}' requires a list value.")
                expr = column.notin_(val)
            elif op == "contains":
                expr = column.ilike(f"%{val}%")
            elif op == "does not contain":
                expr = column.notilike(f"%{val}%")
            elif op == "starts with":
                expr = column.ilike(f"{val}%")
            elif op == "ends with":
                expr = column.ilike(f"%{val}")
            elif op == "is empty":
                # For strings, we might want to check both NULL and empty string,
                # but the prompt specifically says "Implement is empty and is not empty correctly for SQL NULL values. Do not equate NULL with empty string."
                expr = column.is_(None)
            elif op == "is not empty":
                expr = column.isnot(None)
            elif op == "gt" or op == "greater than" or op == "after":
                expr = column > val
            elif op == "gte" or op == "greater than or equal" or op == "on or after":
                expr = column >= val
            elif op == "lt" or op == "less than" or op == "before":
                expr = column < val
            elif op == "lte" or op == "less than or equal" or op == "on or before":
                expr = column <= val
            elif op == "between":
                if not isinstance(val, list) or len(val) != 2:
                    raise ValueError(f"Operator 'between' requires a list of exactly 2 values.")
                expr = column.between(val[0], val[1])
            elif op == "is true":
                expr = column == True
            elif op == "is false":
                expr = column == False
            else:
                raise ValueError(f"Invalid operator: {op}")
            
            expressions.append(expr)

    if not expressions:
        return None

    if ast.logic.upper() == "OR":
        return or_(*expressions)
    else:
        return and_(*expressions)


def apply_sorting(query: Query, sort_rules: List[SortRule]) -> Query:
    for rule in sort_rules:
        if rule.field not in FIELD_REGISTRY:
            raise ValueError(f"Invalid sort field: {rule.field}")
        
        column = FIELD_REGISTRY[rule.field]
        if rule.direction.upper() == "DESC":
            query = query.order_by(desc(column))
        else:
            query = query.order_by(asc(column))
    
    return query

def has_cluster_field(ast: FilterGroup) -> bool:
    """Helper to check if any field requires the Cluster table."""
    for item in ast.conditions:
        if isinstance(item, FilterGroup):
            if has_cluster_field(item):
                return True
        else:
            if item.field in ["cluster_name", "three_r_reason"]:
                return True
    return False


def has_recurrence_field(ast: FilterGroup) -> bool:
    """Helper to check if any field requires the Recurrence table."""
    for item in ast.conditions:
        if isinstance(item, FilterGroup):
            if has_recurrence_field(item):
                return True
        else:
            if item.field in ["problem_candidate"]:
                return True
    return False

