import json
from API import (
    get_req_ensure_label,
    get_req_ensure_music,
    get_req_ensure_session,
    get_req_progression_generation,
    get_req_voices_generation,
    get_req_midihex_generation,
    PseudoMIDI,
    Progression,
    Performance,
    PerformanceRequest,
    AmendmentRequest,
    LabelingRequest,
    PerformanceResponse,
    construct_performance,
    construct_progression,
    construct_session_data,
    construct_user_data,
    construct_label_data,
    construct_path_data,
    construct_performance_data,
    post_multi_requests,
    post_single_request,
)
from API.requests import get_req_progression_amendment
from logsetup import get_logger

logger_scenarios = get_logger("scenarios")
async def generate_progression(full_request: PerformanceRequest) -> PerformanceResponse:
    performance = full_request.performance_object
    
    perf_name = performance.__class__.__name__
    
    if full_request.user_id is not None:
        data_type = "user"
        session_data = construct_user_data(full_request)
    else:
        data_type = "session"
        session_data = construct_session_data(full_request)
    req_ensure_session = get_req_ensure_session(session_data)
    ensured_session = post_single_request(*req_ensure_session)
    logger_scenarios.info(f"Submitted the {data_type} data from request")


    # Alternative if statement somehow breaks the code, hence the try/except
    try:
        progression = construct_progression(performance) # type: ignore
        logger_scenarios.info(f"Parsed a progression from {perf_name}")
    except AttributeError:
        logger_scenarios.info(f"Can't parse a progression from {perf_name}: requesting a new one")
        req_prog = get_req_progression_generation(performance)
        progression_raw = await post_single_request(*req_prog)
        progression = Progression.parse_raw(progression_raw)

    progression_data = construct_path_data(progression)
    req_ensure_path = get_req_ensure_music(progression_data)
    ensured_path = post_single_request(*req_ensure_path)
    logger_scenarios.info(f"Requested and submitted a new path.")    

    req_voice = get_req_voices_generation(performance, progression=progression)
    voices_raw = await post_single_request(*req_voice)
    voices = PseudoMIDI.parse_raw(voices_raw)
    cheetsheet = req_voice[1]

    performance_data = construct_performance_data(progression, cheetsheet, voices)
    req_ensire_perf = get_req_ensure_music(performance_data)
    ensured_perf = post_single_request(*req_ensire_perf)
    logger_scenarios.info(f"Requested and submitted a new voicing.")    

    req_midihex = get_req_midihex_generation(voices)
    midihex_raw = await post_single_request(*req_midihex)
    midihex = json.loads(midihex_raw)
    logger_scenarios.info(f"Requested a new hex-encoded midi.")

    outcoming_performance = construct_performance(
        progression=progression,
        cheet_sheet=cheetsheet,
        hex_blob=midihex,
        pseudo_midi=voices
    )
    logger_scenarios.info(f"Constructed a new performance.")

    await ensured_session
    await ensured_path
    await ensured_perf

    logger_scenarios.info(f"Received all responses from the server.")
    return outcoming_performance

async def amend_progression(full_request: AmendmentRequest, index: int) -> PerformanceResponse:
    old_performance = full_request.performance_object
    
    req_amend_progression = get_req_progression_amendment(old_performance, index)
    new_progression_raw = await post_single_request(*req_amend_progression) # type: str
    new_progression = Progression.parse_raw(new_progression_raw)
    
    
    if full_request.user_id is not None:
        session_data = construct_user_data(full_request)
    else:
        session_data = construct_session_data(full_request)

    req_ensure_session = get_req_ensure_session(session_data)
    ensured_session = post_single_request(*req_ensure_session)

    progression_data = construct_path_data(new_progression)
    req_ensure_path = get_req_ensure_music(progression_data)
    ensured_path = post_single_request(*req_ensure_path)    

    req_voice = get_req_voices_generation(old_performance, progression=new_progression)
    voices_raw = await post_single_request(*req_voice) # type: str
    voices = PseudoMIDI.parse_raw(voices_raw)
    cheetsheet = req_voice[1]

    performance_data = construct_performance_data(new_progression, cheetsheet, voices)
    req_ensire_perf = get_req_ensure_music(performance_data)
    ensured_perf = post_single_request(*req_ensire_perf)

    req_midihex = get_req_midihex_generation(voices)
    midihex_raw = await post_single_request(*req_midihex) # type: str
    midihex = json.loads(midihex_raw)

    outcoming_performance = construct_performance(
        progression=new_progression,
        cheet_sheet=cheetsheet,
        hex_blob=midihex,
        pseudo_midi=voices
    )

    await ensured_session
    await ensured_path
    await ensured_perf

    return outcoming_performance

async def send_labels(labeling_request: LabelingRequest) -> bool:
    """Send labels to the server."""

    if labeling_request.user_id is not None:
        session_data = construct_user_data(labeling_request)
    else:
        session_data = construct_session_data(labeling_request)
    req_ensure_session = get_req_ensure_session(session_data)
    ensured_session = post_single_request(*req_ensure_session)

    label_data = construct_label_data(labeling_request)
    req_label = get_req_ensure_label(label_data)
    try:

        await post_single_request(*req_label)
        await ensured_session
        return True
    except ValueError:
        return False