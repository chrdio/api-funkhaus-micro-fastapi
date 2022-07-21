from typing import Tuple
from pydantic import BaseModel
from .adapter_functions import (
    get_path_data,
    get_performance_data,
    get_session_data,
    get_user_data,
    get_label_data,
    get_progression_request,
    get_cheet_sheet,
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
)
from .endpoints import (
    Endpoint,
    ENDPOINTS,
)

def get_req_progression_generation(performance: Performance) -> Tuple[Endpoint, ProgressionRequest]:
    return (ENDPOINTS["micropathforger/generate"], get_progression_request(performance))

def get_req_progression_amendment(performance: Performance, index: int) -> Tuple[Endpoint, ProgressionRequest]:
    endpoint = ENDPOINTS["micropathforger/amend"]
    endpoint.option = str(index)
    return (endpoint, get_progression_request(performance))