from typing import Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field


class FilterCondition(BaseModel):
    field: str
    operator: str
    value: Any = None


class FilterGroup(BaseModel):
    logic: Literal["AND", "OR"] = "AND"
    conditions: List[Union['FilterCondition', 'FilterGroup']] = Field(default_factory=list)


FilterGroup.model_rebuild()


class SortRule(BaseModel):
    field: str
    direction: Literal["ASC", "DESC", "asc", "desc"] = "ASC"
