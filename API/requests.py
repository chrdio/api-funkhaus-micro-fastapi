from typing import Optional, Tuple, Union
from pydantic import BaseModel
from aiohttp import ClientSession

from API.engine import instant_fire_coroutines, post_single_request
from .adapter_functions import (
    construct_progression_request,
    construct_cheet_sheet,
    construct_progression,
)
from .inner_models import (
    PathData,
    PerformanceData,
    SessionData,
    UserData,
    LabelData,
    PseudoMIDI,
    CheetSheet,
    ProgressionRequest,
    Progression,
)
from .outer_models import (
    Performance,
    GenericRequest,
    LabelingRequest,
    PerformanceResponse,
)
from .endpoints import (
    Endpoint,
    ENDPOINTS,
)

def get_req_progression_generation(performance: Performance) -> Tuple[Endpoint, ProgressionRequest]:
    return (ENDPOINTS["micropathforger/generate"], construct_progression_request(performance))

def get_req_progression_amendment(performance: PerformanceResponse, index: int) -> Tuple[Endpoint, Progression]:
    endpoint = ENDPOINTS["micropathforger/amend"]
    endpoint.option = str(index)
    return (endpoint, construct_progression(performance))

def get_req_voices_generation(performance: Performance, progression: Optional[Progression] = None) -> Tuple[Endpoint, CheetSheet]:
    cheetsheet = construct_cheet_sheet(performance, progression=progression)
    endpoint = ENDPOINTS["microvoicemaster/perform"]
    return (endpoint, cheetsheet)

def get_req_midihex_generation(pseudo: PseudoMIDI) -> Tuple[Endpoint, PseudoMIDI]:
    endpoint = ENDPOINTS["microbureaucrat/savemidi"]
    endpoint.option = 'mid'
    return (endpoint, pseudo)

def get_req_ensure_session(user_session: Union[UserData, SessionData]) -> Tuple[Endpoint, Union[UserData, SessionData]]:
    endpoint = ENDPOINTS["microaccountant/people"]
    return (endpoint, user_session)

def get_req_ensure_music(music: Union[PerformanceData, PathData]) -> Tuple[Endpoint, Union[PerformanceData, PathData]]:
    endpoint = ENDPOINTS["microaccountant/music"]
    return (endpoint, music)

def get_req_ensure_label(label: LabelData) -> Tuple[Endpoint, LabelData]:
    endpoint = ENDPOINTS["microaccountant/data"]
    return (endpoint, label)

ENSUREMENT_REQUEST_METHODS = {
    PerformanceData: get_req_ensure_music,
    PathData: get_req_ensure_music,
    SessionData: get_req_ensure_session,
    UserData: get_req_ensure_session,
    LabelData: get_req_ensure_label,
}

def submit_data(
    *data: Union[UserData, SessionData, PerformanceData, PathData, LabelData],
    storage: set,
    session: ClientSession,
    ) -> None:
    coroutines = [
        post_single_request(*ENSUREMENT_REQUEST_METHODS[type(data)](data), session=session)
        for data in data
        ]
    new_tasks = instant_fire_coroutines(*coroutines)
    storage.update(new_tasks)