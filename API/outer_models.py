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

    key: Optional[NotesInt] = None
    graph: Optional[GraphNames] = None
    
    
class PerformanceResponse(BaseModel):
    class Config:
        use_enum_values = True
    
    key: NotesInt
    graph: GraphNames
    ticket: str
    hex_blob: str
    structures: Sequence[ChordSymbolStructures]
    human_readable: Sequence[Any] = list()
    nodes: Sequence[Node]

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
                'user_id': UUID('00000000-SOME-KNOWN-ID-000000000000'),
            }
        }


class LabelingRequest(GenericRequest):

    class Config:
        use_enum_values = True
        schema_extra = {
            'example': {
                'sess_id': IPv4Address('192.0.0.1'),
                'user_id': UUID('00000000-SOME-KNOWN-ID-000000000000'),
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
                'user_id': UUID('00000000-SOME-KNOWN-ID-000000000000'),
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
                'user_id': UUID('00000000-SOME-KNOWN-ID-000000000000'),
                'performance_object': {
                   "warning": "should be copied verbatim from the response, don't try to specify manually"
                }
            }
        }

    performance_object:  PerformanceResponse