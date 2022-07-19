from ipaddress import IPv4Address
from datetime import datetime
from typing import Optional, Sequence, Any, Tuple
from uuid import UUID
from pydantic import BaseModel, validator, PrivateAttr, Extra

from .enums import NotesInt, ChordSymbolStructures, GraphNames, NodeIDs, PerformanceFlags

class Performance:
    class Config:
        use_enum_values = True

    key: Optional[NotesInt] = None
    graph: Optional[GraphNames] = None
    ticket: Optional[str] = None
    nodes: Sequence[Tuple[NodeIDs, ChordSymbolStructures]] = list()
    human_readable: Optional[Sequence[Any]] = None



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

    performance_object: Performance = Performance()