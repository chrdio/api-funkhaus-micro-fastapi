from typing import Optional, Tuple, Union
from aiohttp import ClientSession

from .engine import instant_fire_coroutines, post_single_request
from .adapter_functions import (
    construct_progression_request,
    construct_cheet_sheet,
    construct_progression,
)
from chrdiotypes.musical import (
    PseudoMIDI,
    CheetSheet,
    ProgressionRequest,
    ProgressionFields,
)
from chrdiotypes.transport import (
    SessionTransport,
    UserTransport,
    LabelTransport,
    )
from .outer_models import (
    Performance,
    PerformanceResponse,
)
from .endpoints import (
    Endpoint,
    ENDPOINTS,
)

def get_req_progression_generation(performance: Union[Performance, PerformanceResponse]) -> Tuple[Endpoint, ProgressionRequest]:
    return (ENDPOINTS["micropathforger/generate"], construct_progression_request(performance))

def get_req_progression_amendment(performance: PerformanceResponse, index: int) -> Tuple[Endpoint, ProgressionFields]:
    endpoint = ENDPOINTS["micropathforger/amend"]
    endpoint.option = str(index)
    return (endpoint, construct_progression(performance))

def get_req_voices_generation(performance: Union[Performance, PerformanceResponse], progression: Optional[ProgressionFields] = None) -> Tuple[Endpoint, CheetSheet]:
    cheetsheet = construct_cheet_sheet(performance, progression=progression)
    endpoint = ENDPOINTS["microvoicemaster/perform"]
    return (endpoint, cheetsheet)

def get_req_midihex_generation(pseudo: PseudoMIDI) -> Tuple[Endpoint, PseudoMIDI]:
    endpoint = ENDPOINTS["microbureaucrat/savemidi"]
    endpoint.option = 'mid'
    return (endpoint, pseudo)

def get_req_ensure_session(user_session: Union[UserTransport, SessionTransport]) -> Tuple[Endpoint, Union[UserTransport, SessionTransport]]:
    endpoint = ENDPOINTS["microaccountant/people"]
    return (endpoint, user_session)

def get_req_ensure_label(label: LabelTransport) -> Tuple[Endpoint, LabelTransport]:
    endpoint = ENDPOINTS["microaccountant/data"]
    return (endpoint, label)

# A legacy endpoint
# def get_req_user_creation(request: SessionTransport) -> Tuple[Endpoint, SessionTransport]:
#     endpoint = ENDPOINTS["microaccountant/createuser"]
#     return (endpoint, request)

ENSUREMENT_REQUEST_METHODS = {
    SessionTransport: get_req_ensure_session,
    UserTransport: get_req_ensure_session,
    LabelTransport: get_req_ensure_label,
}

def submit_data_tasks(
    *data: Union[UserTransport, SessionTransport, LabelTransport],
    storage: set,
    session: ClientSession,
    ) -> None:
    coroutines = [
        post_single_request(*ENSUREMENT_REQUEST_METHODS[type(data)](data), session=session)
        for data in data
        ]
    new_tasks = instant_fire_coroutines(*coroutines)
    storage.update(new_tasks)