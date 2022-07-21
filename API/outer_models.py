import random
from ipaddress import IPv4Address
from datetime import datetime
from typing import Optional, Sequence, Any, Tuple, Union
from uuid import UUID
from pydantic import BaseModel, validator, PrivateAttr, Extra, Field

from API.inner_models import Node

from .enums import NotesInt, ChordSymbolStructures, GraphNames, NodeIDs, PerformanceFlags

class Performance(BaseModel):
    class Config:
        use_enum_values = True

    key: Optional[NotesInt] = None
    graph: Optional[GraphNames] = None
    
    
class PerformanceResponse(Performance):
    class Config:
        use_enum_values = True
    
    key: NotesInt
    graph: GraphNames
    nodes: Sequence[Node]
    structures: Sequence[ChordSymbolStructures]
    ticket: str
    hex_blob: str
    human_readable: Sequence[Any]

    @classmethod
    def from_performance(cls, performance: Performance):
        perf_dict = performance.dict()
        has_all_values = all(
            perf_dict.get(key)
            for key in [
                'key',
                'graph',
                'nodes',
                'structures',
                'hex_blob',
                'human_readable'
                ]
        )
        if has_all_values:
            return cls(**perf_dict)
        else:
            raise ValueError('Performance is missing required values to create a PerformanceResponse')




class GenericRequest(BaseModel):
    class Config:
        extra = Extra.ignore
        underscore_attrs_are_private = True

    session_id: IPv4Address
    user_id: Optional[UUID] = None
    _localtime: datetime = PrivateAttr(default_factory=datetime.now)


class LabelingRequest(GenericRequest):

    class Config:
        use_enum_values = True

    ticket: str
    flag: PerformanceFlags

    _various: Optional[str] = PrivateAttr(default=None)

    @validator("ticket")
    def ticket_format_valid(cls, v):
        """Checks if ticket consists of numeric characters."""

        assert v[1:].isnumeric()
        return v


class PerformanceRequest(GenericRequest):
    """A data model with adapters."""

    class Config:
        use_enum_values = True

    performance_object: Union[Performance, PerformanceResponse] = Performance()

class AmendmentRequest(PerformanceRequest):

    class Config:
        use_enum_values = True

    performance_object:  PerformanceResponse