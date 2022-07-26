from ipaddress import IPv4Address
from datetime import datetime
from typing import Optional, Sequence, Any, Tuple, Union
from uuid import UUID
from pydantic import(
    BaseModel,
    root_validator,
    PrivateAttr,
    Extra,
    Field,
)

from API.inner_models import Node

from .enums import (
    NotesInt,
    NotesSymbol,
    ChordSymbolStructures,
    GraphNames,
    PerformanceFlags,
    ChordTypes,
    StructureSymbols,
    StructureValues,
)

class Performance(BaseModel):
    class Config:
        use_enum_values = True
        allow_extra = Extra.forbid

    key: Optional[NotesInt] = Field(
        default=None,
        title="Key",
        description="The 0-11 halftone that represents a tonal center.",
        ge=0,
        le=11,
        example=4,
        )
    graph: Optional[GraphNames] = Field(
        default=None,
        title="Graph",
        description="Graphs name, usually corresponds to a mode.",
        example="major_graph",
    )
    
    
class PerformanceResponse(BaseModel):
    class Config:
        title = "Progression/Performance Response Object"
        use_enum_values = True
    
    key: NotesInt = Field(
        ...,
        title="Key",
        description="The 0-11 halftone that represents a tonal center.",
        ge=0,
        le=11,
        example=4,
        )
    graph: GraphNames = Field(
        ...,
        title="Graph",
        description="Graphs name, usually corresponds to a mode.",
        example="major_graph",
    )
    ticket: str = Field(
        ...,
        title="Ticket",
        description="A unique identifier for this performance.",
        example="-123581321345589",
    )
    hex_blob: str = Field(
        ...,
        title="MIDI",
        description="A hex-encoded blob of MIDI data.",
        example="4d54...2f00",
    )
    structures: Sequence[ChordSymbolStructures] = Field(
        ...,
        title="Structures",
        description="A corresponding list of interval structures for each chord.",
        example=["M4Q5O8", "m3Q5O8", "m3Q5O8", "M4Q5O8"],
    )
    human_readable: Sequence[Tuple[str, str, Union[int, None]]] = Field(
        default_factory=list,
        title="Human-readable representation",
        description="A list of tuples, each containing a chord symbol, a chord type, and a chord quality.",
        example=[("C", "major", None), ("D", "minor", None), ("E", "minor", None), ("F", "major", None)],
    )
    nodes: Sequence[Node] = Field(
        ...,
        title="Chords",
        description="A list of chord charateristics.",
        example=[
            Node(
                node_id='NORM1+',
                mode=True,
                tonality=True,
                gravity=0,
                base=0,
            ),
            Node(
                node_id='SHRP2-',
                mode=True,
                tonality=False,
                gravity=-3,
                base=2,
            ),
            Node(
                node_id='SHRP3-',
                mode=True,
                tonality=False,
                gravity=1,
                base=4,
            ),
            Node(
                node_id='NORM4+',
                mode=True,
                tonality=True,
                gravity=2,
                base=5,
            ),
        ],
    )

    @root_validator
    def construct_human_readable(cls, values):
        if (values.get('nodes') is not None) and (not values.get('human_readable')):
            # If this check isn't here, somehow it tries to validate Performance instance,
            # which is in Union[Performance, PerformanceResponse] on PerformanceRequest.
        
            names_and_types = [(
                    NotesSymbol[NotesInt((node.base + values["key"])%12).name].value,
                    ChordTypes(node.node_id[-1]).name
                    )
                for node in values["nodes"]
                ]
            flavors = [
                StructureValues[StructureSymbols(structure[-1]).name].value  # type: ignore Uses enum values
                for structure in values["structures"]
            ]
            values["human_readable"] = list(zip(*zip(*names_and_types), flavors))
            
        return values
        
    
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

    sess_id: IPv4Address
    user_id: Optional[UUID] = None
    _localtime: datetime = PrivateAttr(default_factory=datetime.now)

    class Config:
        underscore_attrs_are_private = True
        schema_extra = {
            'example': {
                'sess_id': IPv4Address('192.0.0.1'),
                'user_id': '00000000-SOME-KNOWN-ID-000000000000',
            }
        }


class LabelingRequest(GenericRequest):

    class Config:
        use_enum_values = True
        schema_extra = {
            'example': {
                'sess_id': IPv4Address('192.0.0.1'),
                'user_id': '00000000-SOME-KNOWN-ID-000000000000',
                'ticket': '-123581321345589',
                'flag': PerformanceFlags.served.value,
            }
        }

    ticket: str
    flag: PerformanceFlags

    _various: Optional[str] = PrivateAttr(default=None)


class PerformanceRequest(GenericRequest):
    """A data model with adapters."""

    class Config:
        use_enum_values = True
        schema_extra = {
            'example': {
                'sess_id': IPv4Address('192.0.0.1'),
                'user_id': '00000000-SOME-KNOWN-ID-000000000000',
                'performance_object': {},
                }
            }


    performance_object: Union[PerformanceResponse, Performance] = Performance()

class AmendmentRequest(PerformanceRequest):

    class Config:
        use_enum_values = True
        schema_extra = {
            'example': {
                'sess_id': IPv4Address('192.0.0.1'),
                'user_id': '00000000-SOME-KNOWN-ID-000000000000',
                'performance_object': {
                   "warning": "should be copied verbatim from the response, don't try to specify manually"
                }
            }
        }

    performance_object:  PerformanceResponse