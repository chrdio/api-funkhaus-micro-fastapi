from ipaddress import IPv4Address
import random
from uuid import UUID
from pydantic import BaseModel, PrivateAttr, root_validator, Field, validator
from typing import List, Optional, Sequence, Tuple
from datetime import datetime
from .enums import ChordIntervalStructures, NotesInt, PerformanceFlags, GraphNames


class PathData(BaseModel):
    nodes: List[Tuple[str, str]]
    graph_name: str


class PerformanceData(BaseModel):
    perf_id: str
    key: int
    path_nodes: List[Tuple[str, str]]


class SessionData(BaseModel):
    sess_id: IPv4Address


class UserData(BaseModel):
    user_id: UUID
    sess_id: IPv4Address


class LabelData(BaseModel):
    _localtime: datetime = PrivateAttr(default_factory=datetime.now)
    sess_id: IPv4Address
    perf_id: str
    flag: PerformanceFlags
    user_id: Optional[UUID] = None
    _various: Optional[str] = None

    class Config:
        use_enum_values = True
        underscore_attrs_are_private = True


class PseudoMIDI(BaseModel):
    voices: Sequence[Sequence[int]]
    ticket: str


class CheetSheet(BaseModel):
    info: List[Tuple[str, str]]
    structures: List[List[int]]
    special_cases: List[bool]
    bases: List[int]
    key: Optional[int] = Field(default_factory=lambda: random.randint(0, 11))
    #ordering: str (is randomized on site)

    @root_validator(pre=True)
    def check_length(cls, values):
        if values.get('key') is None:
            values['key'] = random.randint(0, 11)
        equal_length = len(values['structures']) == len(values['special_cases']) == len(values['bases'])
        if not equal_length:
            raise ValueError('All lists must be of equal length')

        return values

class Node(BaseModel):
    node_id: str
    mode: bool
    tonality: bool
    gravity: int
    base: int


class Progression(BaseModel):
    graph: GraphNames
    nodes: Sequence[Node]
    structures: Sequence[ChordIntervalStructures]
    orderings: Optional[Tuple[str, ...]] = None
    changeabilities: Sequence[bool]

    class Config:
        use_enum_values = True

    def __hash__(self) -> int:
        return hash((self.nodes, self.graph, self.structures))


class ProgressionRequest(BaseModel):
    graph: Optional[str] = None

    class Config:
        use_enum_values = True