from ipaddress import IPv4Address
from datetime import datetime
from typing import Optional, Sequence, Tuple, Union
from pydantic import(
    root_validator,
    PrivateAttr,
    Field,
    EmailStr,
    Extra,
    BaseModel
)

from chrdiotypes.data_enums import (
    ChordGravities,
    NodeIDs,
    NotesInt,
    NotesSym,
    ChordSymbolStructures,
    GraphNames,
    PerformanceFlags,
    ChordTypes,
    StructureSymbols,
    StructureValues,
    enum_encoders,
)

from chrdiotypes.transport import GenericUser
from chrdiotypes.musical import NodeFields


class User(GenericUser):
    class Config:
        json_encoders=enum_encoders
        title = "Generic User Object"
    
    email: EmailStr = Field(
        ...,
        title="Email",
        description="The user's email address.",
        example="ada.lovelace@aol.com",
    )

    name_given: str = Field(
        ...,
        title="Given Name",
        description="The given name of the user.",
        example="Ada",
    )
    name_family: str = Field(
        ...,
        title="Family Name",
        description="The family name of the user.",
        example="Lovelace",
    )

class Performance(BaseModel):
    class Config:
        json_encoders=enum_encoders
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
        json_encoders=enum_encoders
        title = "Progression/Performance Response Object"
    
    key: NotesInt = Field(
        ...,
        title="Key",
        description="The 0-11 halftone that represents a tonal center.",
        ge=0,
        le=11,
        example=0,
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
        example=["M3Q5O8", "m3Q5O8", "m3Q5O8", "M3Q5O8"],
    )
    changeabilities: Sequence[bool] = Field(
        ...,
        title="Changeabilities",
        description="A list of booleans, each representing whether a chord can be changed.",
        example=[True, True, True, True],
    )
    human_readable: Sequence[Tuple[str, str, Union[int, None]]] = Field(
        default_factory=list,
        title="Human-readable representation",
        description="A list of tuples, each containing a chord symbol, a chord type, and a chord quality.",
        example=[("C", "maj", None), ("D", "min", None), ("E", "min", None), ("F", "maj", None)],
    )
    nodes: Sequence[NodeFields] = Field(
        ...,
        title="Chords",
        description="A list of chord charateristics.",
        example=[
            NodeFields(
                node_id=NodeIDs('NORM1+'),
                mode=True,
                tonality=True,
                gravity=ChordGravities(0),
                base=NotesInt(0),
            ),
            NodeFields(
                node_id=NodeIDs('SHRP2-'),
                mode=True,
                tonality=False,
                gravity=ChordGravities(-3),
                base=NotesInt(2),
            ),
            NodeFields(
                node_id=NodeIDs('SHRP3-'),
                mode=True,
                tonality=False,
                gravity=ChordGravities(1),
                base=NotesInt(4),
            ),
            NodeFields(
                node_id=NodeIDs('NORM4+'),
                mode=True,
                tonality=True,
                gravity=ChordGravities(2),
                base=NotesInt(5),
            ),
        ],
    )


    @root_validator
    def construct_human_readable(cls, values):
        if (values.get('nodes') is not None) and (not values.get('human_readable')):
            # If this check isn't here, somehow it tries to validate Performance instance,
            # which is in Union[Performance, PerformanceResponse] on PerformanceRequest.
        
            names_and_types = [(
                    NotesSym[NotesInt((node.base + values["key"])%12).name].value,
                    ChordTypes(node.node_id.value[-1]).name.lower()
                    )
                for node in values["nodes"]
                ]
            flavors = [
                StructureValues[StructureSymbols(structure.value[-1]).name].value
                for structure in values["structures"]
            ]
            values["human_readable"] = list(zip(*zip(*names_and_types), flavors))
            
        return values
        
    
    # @classmethod
    # def from_performance(cls, performance: Performance):
    #     perf_dict = performance.dict()
    #     has_all_values = all(
    #         perf_dict.get(key)
    #         for key in [
    #             'key',
    #             'graph',
    #             'nodes',
    #             'structures',
    #             'hex_blob',
    #             'human_readable'
    #             ]
    #     )
    #     if has_all_values:
    #         return cls(**perf_dict)
    #     else:
    #         raise ValueError('Performance is missing required values to create a PerformanceResponse')


class GenericRequest(BaseModel):

    sess_id: IPv4Address
    user_object: Optional[User] = None
    _localtime: datetime = PrivateAttr(default_factory=datetime.now)

    class Config:
        json_encoders=enum_encoders
        underscore_attrs_are_private = True
        schema_extra = {
            'example': {
                'sess_id': IPv4Address('192.0.0.1'),
                'user_object': User(email=EmailStr("ada.lovelace@aol.com"), name_given="Ada", name_family="Lovelace"),
            }
        }


class LabelingRequest(GenericRequest):

    class Config:
        json_encoders=enum_encoders
        schema_extra = {
            'example': {
                'sess_id': IPv4Address('192.0.0.1'),
                'user_object': User(email=EmailStr("ada.lovelace@aol.com"), name_given="Ada", name_family="Lovelace"),
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
        json_encoders=enum_encoders
        schema_extra = {
            'example': {
                'sess_id': IPv4Address('192.0.0.1'),
                'user_object': User(email=EmailStr("ada.lovelace@aol.com"), name_given="Ada", name_family="Lovelace"),
                'performance_object': {},
                }
            }


    performance_object: Union[PerformanceResponse, Performance] = Performance()

class AmendmentRequest(PerformanceRequest):

    class Config:
        json_encoders=enum_encoders
        schema_extra = {
            'example': {
                'sess_id': IPv4Address('192.0.0.1'),
                'user_object': User(email=EmailStr("ada.lovelace@aol.com"), name_given="Ada", name_family="Lovelace"),
                'performance_object': {
                   "warning": "should be copied verbatim from the response, don't try to specify manually"
                }
            }
        }

    performance_object:  PerformanceResponse