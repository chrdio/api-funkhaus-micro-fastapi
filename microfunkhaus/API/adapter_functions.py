from typing import Dict, Optional, Union
from pydantic import EmailStr
from .inner_models import (
    PathData,
    PerformanceData,
    PseudoMIDI,
    SessionData,
    UserData, 
    LabelData,
    ProgressionRequest, 
    CheetSheet,
    Progression
)
from .enums import (
    NotesInt,
    ChordSymbolStructures,
    ChordIntervalStructures,
)
from .outer_models import (
    Performance,
    GenericRequest,
    LabelingRequest,
    PerformanceResponse
)


def construct_path_data(progression: Progression) -> PathData:
    graph = progression.graph
    node_names = [node.node_id for node in progression.nodes]
    structure_names = [
        ChordSymbolStructures[ChordIntervalStructures(structure).name].value # type: ignore Uses enum values
        for structure in progression.structures
        ] 
    nodes = list(zip(node_names, structure_names))
    return PathData(nodes=nodes, graph_name=graph)  # type: ignore Uses enum values


def construct_voicing_data(progression: Progression, cheet_sheet: CheetSheet, pseudo_midi: PseudoMIDI) -> PerformanceData:
    key = cheet_sheet.key
    node_names = [node.node_id for node in progression.nodes]
    structure_names = [
        ChordSymbolStructures[ChordIntervalStructures(structure).name].value # type: ignore Uses enum values
        for structure in progression.structures
        ] 
    path_nodes = list(zip(node_names, structure_names))
    perf_id = pseudo_midi.ticket
    return PerformanceData(perf_id=perf_id, key=key, path_nodes=path_nodes) # type: ignore Key is instaniated if None


def construct_session_data(request: GenericRequest) -> SessionData:
    return SessionData(sess_id=request.sess_id)

def construct_user_data(request: GenericRequest) -> UserData:
    if request.user_object:
        return UserData(user_object=request.user_object, sess_id=request.sess_id)
    else:
        raise ValueError('No user data provided')

def construct_label_data(request: LabelingRequest) -> LabelData:
    if request.user_object:
        return LabelData(sess_id=request.sess_id, perf_id=request.ticket, flag=request.flag, user_email=EmailStr(request.user_object.email))
    else:
        raise ValueError('No user data provided')

def construct_progression_request(performance: Union[Performance, PerformanceResponse]) -> ProgressionRequest:
    return ProgressionRequest(graph=performance.graph)  # type: ignore Uses enum values

def construct_cheet_sheet(performance: Union[PerformanceResponse, Performance], progression: Optional[Progression] = None) -> CheetSheet:
    if progression:
        structures = progression.structures
        bases = [node.base for node in progression.nodes]
        node_names = [node.node_id for node in progression.nodes]
        structure_names = [
                ChordSymbolStructures[ChordIntervalStructures(structure).name].value # type: ignore Uses enum values
                for structure in progression.structures
                ]
    else:
        try:
            bases = [node.base for node in performance.nodes]   # type: ignore Uses enum values
            structures = [ChordIntervalStructures[struc].value for struc in performance.structures] # type: ignore Uses enum values
            node_names = [node.node_id for node in performance.nodes] # type: ignore
            structure_names = performance.structures # type: ignore
        except AttributeError:
            raise ValueError('Not enough data to generate a CheetSheet.')
    
    path_nodes = list(zip(node_names, structure_names))

    key = performance.key
    special_cases = [14 in struc for struc in structures]   # type: ignore Uses enum values
    return CheetSheet(info=path_nodes, structures=structures, special_cases=special_cases, bases=bases, key=key)     # type: ignore Uses enum values

def construct_progression(performance: PerformanceResponse) -> Progression:
    nodes = [
        node
        for node in performance.nodes
        ]
    structures = [
        ChordIntervalStructures[ChordSymbolStructures(struc).name]
        for struc in performance.structures
        ]
    return Progression(graph=performance.graph, nodes=nodes, structures=structures, changeabilities=performance.changeabilities)

def construct_performance(*, progression: Progression, cheet_sheet: CheetSheet, pseudo_midi: PseudoMIDI, hex_blob: str) -> PerformanceResponse:
    structure_names = [ChordSymbolStructures(ChordIntervalStructures(structure).name) for structure in progression.structures] # type: ignore Uses enum values
    performance = PerformanceResponse(
        graph=progression.graph,
        key=NotesInt(cheet_sheet.key),
        nodes=progression.nodes,
        hex_blob=hex_blob,
        human_readable=list(list()),
        structures=structure_names,
        ticket=pseudo_midi.ticket,
        changeabilities=progression.changeabilities,
        )
    
    return performance