import random
from typing import Optional, Union
from chrdiotypes.transport import (
    GenericUser,
    PathTransport,
    PerformanceTransport,
    SessionTransport,
    UserTransport,
    LabelTransport,
)
from chrdiotypes.musical import (
    PseudoMIDI,
    ProgressionRequest,
    CheetSheet,
    ProgressionFields,
)
from chrdiotypes.data_enums import (
    NotesInt,
    ChordSymbolStructures,
    ChordIntervalStructures,
)
from .outer_models import (
    Performance,
    GenericRequest,
    LabelingRequest,
    PerformanceResponse,
)


def construct_path_data(progression: ProgressionFields) -> PathTransport:
    """Uses the specified in ProgressionFields data
    to construct a respective PathTransport API-native instance.
    """

    node_names = tuple(node.node_id for node in progression.nodes)
    structure_names = tuple(
        ChordSymbolStructures[ChordIntervalStructures(structure).name]
        for structure in progression.structures
    )
    nodes = tuple(zip(node_names, structure_names))
    return PathTransport(nodes=nodes, graph_name=progression.graph)


def construct_voicing_data(
    progression: ProgressionFields, cheet_sheet: CheetSheet, pseudo_midi: PseudoMIDI
    ) -> PerformanceTransport:
    """Uses the specified in ProgressionFields, CheetSheet and PseudoMIDI data
    to construct a respective PerformanceTransport API-native instance.
    """

    node_names = tuple(node.node_id for node in progression.nodes)
    structure_names = tuple(
        ChordSymbolStructures[ChordIntervalStructures(structure).name]
        for structure in progression.structures
    )
    path_nodes = tuple(zip(node_names, structure_names))
    perf_id = pseudo_midi.ticket
    perf = PerformanceTransport(
        perf_id=perf_id, key=cheet_sheet.key, path_nodes=path_nodes
    )
    return perf


def construct_session_data(request: GenericRequest) -> SessionTransport:
    """Uses the specified in GenericRequest session ID
    to construct a respective SessionTransport API-native instance.
    """

    return SessionTransport(sess_id=request.sess_id)


def construct_user_data(request: GenericRequest) -> UserTransport:
    """Uses the specified in GenericRequest user data
    to construct a respective SessionTransport API-native instance.
    Raises ValueError if the user data is absent.
    """

    if request.user_object:
        user_object = GenericUser.parse_raw(request.user_object.json())
        return UserTransport(user_object=user_object, sess_id=request.sess_id)
    else:
        raise ValueError("No user data provided")


def construct_label_data(request: LabelingRequest) -> LabelTransport:
    """Uses the specified in LabelingRequest data
    to construct a respective LabelTransport API-native instance.
    """

    if request.user_object:
        mailbox = str(request.user_object.email)
        return LabelTransport(
            sess_id=request.sess_id,
            perf_id=request.ticket,
            flag=request.flag,
            email=mailbox,
        )
    else:
        return LabelTransport(
            sess_id=request.sess_id, perf_id=request.ticket, flag=request.flag
        )


def construct_progression_request(
    performance: Union[Performance, PerformanceResponse]
    ) -> ProgressionRequest:
    """Uses the specified in Performance data
    to construct a respective ProgressionRequest
    expected by the 'micropathforger' service.
    """

    return ProgressionRequest(graph=performance.graph)  # type: ignore Handled in the receiving side (Graph is randomized if None)


def construct_cheet_sheet(
    performance: Union[PerformanceResponse, Performance],
    progression: Optional[ProgressionFields] = None,
    ) -> CheetSheet:
    """Uses the specified in ProgressionFields & Performance data
    to construct a respective CheetSheet
    expected by the 'microvoicemaster' service.

    Tries to do the same based on PerformanceResponse,
    if ProgressionFields is absent.

    Raises ValueError on failure.
    """

    if progression:
        structures = progression.structures
        bases = [node.base for node in progression.nodes]
        node_names = tuple(node.node_id for node in progression.nodes)
        converted_structures = tuple(
            ChordSymbolStructures[structure.name]
            for structure in progression.structures
        )
    else:
        try:
            bases = [node.base for node in performance.nodes]  # type: ignore
            structures = [ChordIntervalStructures[struc.name] for struc in performance.structures]  # type: ignore
            node_names = [node.node_id for node in performance.nodes]  # type: ignore
            converted_structures = tuple(x for x in performance.structures)  # type: ignore
        except AttributeError:
            raise ValueError("Not enough data to generate a CheetSheet.")

    path_nodes = list(zip(node_names, converted_structures))
    key = performance.key
    if key is None:
        key = random.choice(tuple(NotesInt))
    special_cases = [struc.value[1] for struc in structures]
    chsh = CheetSheet(
        info=path_nodes,
        structures=structures,
        special_cases=special_cases,
        bases=bases,
        key=key,
    )
    return chsh


def construct_progression(performance: PerformanceResponse) -> ProgressionFields:
    """Uses the specified in PerformanceResponse data
    to construct a respective
    ProgressionFields API-native instance.
    """

    nodes = tuple(performance.nodes)
    structures = [
        ChordIntervalStructures[ChordSymbolStructures(struc).name]
        for struc in performance.structures
    ]
    progression = ProgressionFields(
        graph=performance.graph,
        nodes=nodes,
        structures=structures,
        changeabilities=performance.changeabilities,
    )
    return progression


def construct_performance(
    *,
    progression: ProgressionFields,
    cheet_sheet: CheetSheet,
    pseudo_midi: PseudoMIDI,
    hex_blob: str
) -> PerformanceResponse:
    """Combines data from various microservices into a PerformanceResponse."""

    symbol_structures = [
        ChordSymbolStructures[structure.name] for structure in progression.structures
    ]
    performance = PerformanceResponse.construct(
        graph=progression.graph,
        key=cheet_sheet.key,
        nodes=progression.nodes,
        hex_blob=hex_blob,
        human_readable=list(list()),  # Handled by validation
        structures=symbol_structures,
        ticket=pseudo_midi.ticket,
        changeabilities=progression.changeabilities,
    )

    return performance
