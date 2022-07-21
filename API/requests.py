from typing import Optional, Tuple, Union
from pydantic import BaseModel
from .adapter_functions import (
    construct_progression_request,
    construct_cheet_sheet,
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

def get_req_progression_amendment(performance: Performance, index: int) -> Tuple[Endpoint, ProgressionRequest]:
    endpoint = ENDPOINTS["micropathforger/amend"]
    endpoint.option = str(index)
    return (endpoint, construct_progression_request(performance))

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