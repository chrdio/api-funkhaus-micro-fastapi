from typing import Dict, Optional
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
    GraphNames,
    NodeIDs,
    PerformanceFlags,
    NodeBase
)
from .outer_models import (
    Performance,
    GenericRequest,
    LabelingRequest,
    PerformanceResponse
)


def get_path_data(progression: Progression) -> PathData:
    graph = progression.graph
    node_names = [node.node_id for node in progression.nodes]
    structure_names = [
        ChordSymbolStructures[structure].value # type: ignore Uses enum values
        for structure in progression.structures
        ] 
    nodes = list(zip(node_names, structure_names))
    return PathData(nodes=nodes, graph_name=graph)  # type: ignore Uses enum values


def get_performance_data(progression: Progression, cheet_sheet: CheetSheet, pseudo_midi: PseudoMIDI) -> PerformanceData:
    key = cheet_sheet.key
    node_names = [node.node_id for node in progression.nodes]
    structure_names = [
        ChordSymbolStructures[structure].value # type: ignore Uses enum values
        for structure in progression.structures
        ] 
    path_nodes = list(zip(node_names, structure_names))
    perf_id = pseudo_midi.ticket
    return PerformanceData(perf_id=perf_id, key=key, path_nodes=path_nodes)


def get_session_data(request: GenericRequest) -> SessionData:
    return SessionData(sess_id=request.session_id)

def get_user_data(request: GenericRequest) -> UserData:
    if request.user_id:
        return UserData(user_id=request.user_id, sess_id=request.session_id)
    else:
        raise ValueError('No user ID provided')

def get_label_data(request: LabelingRequest) -> LabelData:
    return LabelData(sess_id=request.session_id, perf_id=request.ticket, flag=request.flag, user_id=request.user_id)

def get_progression_request(performance: Performance) -> ProgressionRequest:
    return ProgressionRequest(graph=performance.graph)  # type: ignore Uses enum values

def get_cheet_sheet(performance: PerformanceResponse, progression: Optional[Progression] = None) -> CheetSheet:
    if progression:
        structures = progression.structures
        bases = [node.base for node in progression.nodes]
    elif performance.nodes:
        bases = [NodeBase[NodeIDs(node[0])].value for node in performance.nodes]   # type: ignore Uses enum values
        structures = [ChordIntervalStructures[node[1]].value for node in performance.nodes] # type: ignore Uses enum values
    else:
        raise ValueError('No nodes or progression provided')
    
    key = performance.key
    special_cases = [14 in struc for struc in structures]   # type: ignore Uses enum values
    chsh = CheetSheet(structures=structures, special_cases=special_cases, bases=bases, key=key)     # type: ignore Uses enum values
    return chsh

def get_performance(progression: Progression, cheetsheet: CheetSheet, hex_blob: str) -> PerformanceResponse:
    node_names = [NodeIDs(node.node_id) for node in progression.nodes]
    structure_names = [ChordSymbolStructures(ChordIntervalStructures(structure).name) for structure in progression.structures] # type: ignore Uses enum values
    nodes = list(zip(node_names, structure_names))
    performance = PerformanceResponse(
        graph=progression.graph,
        key=NotesInt(cheetsheet.key),
        nodes=nodes,
        hex_blob=hex_blob,
        human_readable=list(list())
        )
    
    return performance