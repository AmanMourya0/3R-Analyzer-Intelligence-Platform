import pytest
from sqlalchemy import select
from sqlalchemy.orm import Query
from app.schemas.filter_ast import FilterGroup, FilterCondition
from app.services.query_builder import build_filter_expression, FIELD_REGISTRY
from app.database.incident_model import Incident

def test_query_builder_single_condition():
    ast = FilterGroup(logic="AND", conditions=[
        FilterCondition(field="priority", operator="eq", value="P1")
    ])
    expr = build_filter_expression(ast)
    assert expr is not None

def test_query_builder_or_logic():
    ast = FilterGroup(logic="OR", conditions=[
        FilterCondition(field="priority", operator="eq", value="P1"),
        FilterCondition(field="priority", operator="eq", value="P2")
    ])
    expr = build_filter_expression(ast)
    assert expr is not None

def test_query_builder_nested_logic():
    ast = FilterGroup(logic="AND", conditions=[
        FilterGroup(logic="OR", conditions=[
            FilterCondition(field="priority", operator="eq", value="P1"),
            FilterCondition(field="priority", operator="eq", value="P2")
        ]),
        FilterCondition(field="three_r_category", operator="eq", value="RUNNER")
    ])
    expr = build_filter_expression(ast)
    assert expr is not None

def test_query_builder_null_semantics():
    ast_empty = FilterGroup(logic="AND", conditions=[
        FilterCondition(field="assigned_group", operator="is empty")
    ])
    expr = build_filter_expression(ast_empty)
    # Testing that it generates an IS NULL expression
    assert "IS NULL" in str(expr) or "is_none" in str(expr) or "assigned_group IS NULL" in str(expr.compile(compile_kwargs={"literal_binds": True}))

    ast_not_empty = FilterGroup(logic="AND", conditions=[
        FilterCondition(field="assigned_group", operator="is not empty")
    ])
    expr2 = build_filter_expression(ast_not_empty)
    assert "IS NOT NULL" in str(expr2) or "isnot(None)" in str(expr2) or "assigned_group IS NOT NULL" in str(expr2.compile(compile_kwargs={"literal_binds": True}))

def test_invalid_field_raises():
    ast = FilterGroup(logic="AND", conditions=[
        FilterCondition(field="invalid_field", operator="eq", value="foo")
    ])
    with pytest.raises(ValueError, match="Invalid field"):
        build_filter_expression(ast)

def test_invalid_operator_raises():
    ast = FilterGroup(logic="AND", conditions=[
        FilterCondition(field="priority", operator="magical_op", value="foo")
    ])
    with pytest.raises(ValueError, match="Invalid operator"):
        build_filter_expression(ast)
