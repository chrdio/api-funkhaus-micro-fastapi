import json
import asyncio
from aiohttp import ClientSession
from API import (
    get_req_progression_generation,
    get_req_progression_amendment,
    get_req_voices_generation,
    submit_data_tasks,
    PseudoMIDI,
    Progression,
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
    construct_voicing_data,
    post_multi_requests,
    post_single_request,
    get_req_midihex_generation,
)
from logsetup import get_logger

logger_generator = get_logger("generate_performance")
async def generate_progression(full_request: PerformanceRequest) -> PerformanceResponse:
    local_session = ClientSession()
    task_chest = set()
    performance = full_request.performance_object
    
    perf_name = performance.__class__.__name__
    
    if full_request.user_id is not None:
        data_type = "user"
        session_data = construct_user_data(full_request)
    else:
        data_type = "session"
        session_data = construct_session_data(full_request)
    submit_data_tasks(session_data, storage=task_chest, session=local_session)
    # ensured_session.add_done_callback(task_chest.discard)
    logger_generator.info(f"Submitted the {data_type} data from request")


    # Alternative if statement somehow breaks the code, hence the try/except
    try:
        progression = construct_progression(performance) # type: ignore
        logger_generator.info(f"Parsed a progression from {perf_name}")
    except AttributeError:
        logger_generator.info(f"Can't parse a progression from {perf_name}: requesting a new one")
        req_prog = get_req_progression_generation(performance)
        progression_raw = await post_single_request(*req_prog, session=local_session)
        progression = Progression.parse_raw(progression_raw) # type: ignore

    
    req_voice = get_req_voices_generation(performance, progression=progression)
    voices_raw = await post_single_request(*req_voice, session=local_session)
    voices = PseudoMIDI.parse_raw(voices_raw) # type: ignore
    cheetsheet = req_voice[1] 
    
    progression_data = construct_path_data(progression)
    voicing_data = construct_voicing_data(progression, cheetsheet, voices)
    submit_data_tasks(progression_data, voicing_data, storage=task_chest, session=local_session)

    req_midihex = get_req_midihex_generation(voices)
    midihex_raw = await post_single_request(*req_midihex, session=local_session)
    midihex = json.loads(midihex_raw) # type: ignore
    logger_generator.info(f"Requested a new hex-encoded midi.")

    outcoming_performance = construct_performance(
        progression=progression,
        cheet_sheet=cheetsheet,
        hex_blob=midihex,
        pseudo_midi=voices
    )
    logger_generator.info(f"Constructed a new performance.")

    await asyncio.gather(*task_chest)
    del task_chest
    await local_session.close()
    logger_generator.info(f"Received all responses from the server.")
    return outcoming_performance

async def amend_progression(full_request: AmendmentRequest, index: int) -> PerformanceResponse:
    old_performance = full_request.performance_object
    local_session = ClientSession()
    task_chest = set()

    
    req_amend_progression = get_req_progression_amendment(old_performance, index)
    new_progression_raw = await post_single_request(*req_amend_progression, session=local_session)
    new_progression = Progression.parse_raw(new_progression_raw) # type: ignore
    
    
    if full_request.user_id is not None:
        session_data = construct_user_data(full_request)
    else:
        session_data = construct_session_data(full_request)
    progression_data = construct_path_data(new_progression)
    submit_data_tasks(session_data, progression_data, storage=task_chest, session=local_session)

    req_voice = get_req_voices_generation(old_performance, progression=new_progression)
    voices_raw = await post_single_request(*req_voice, session=local_session)
    voices = PseudoMIDI.parse_raw(voices_raw) # type: ignore
    cheetsheet = req_voice[1]

    voicing_data = construct_voicing_data(new_progression, cheetsheet, voices)
    submit_data_tasks(voicing_data, storage=task_chest, session=local_session)

    req_midihex = get_req_midihex_generation(voices)
    midihex_raw = await post_single_request(*req_midihex, session=local_session)
    midihex = json.loads(midihex_raw) # type: ignore

    outcoming_performance = construct_performance(
        progression=new_progression,
        cheet_sheet=cheetsheet,
        hex_blob=midihex,
        pseudo_midi=voices
    )

    await asyncio.gather(*task_chest)
    del task_chest
    await local_session.close()
    return outcoming_performance


async def send_labels(labeling_request: LabelingRequest) -> bool:
    local_session = ClientSession()
    task_chest = set()

    if labeling_request.user_id is not None:
        session_data = construct_user_data(labeling_request)
    else:
        session_data = construct_session_data(labeling_request)
    submit_data_tasks(session_data, storage=task_chest, session=local_session)
    label_data = construct_label_data(labeling_request)
    submit_data_tasks(label_data, storage=task_chest, session=local_session)


    await asyncio.gather(*task_chest)
    del task_chest
    await local_session.close()
    return True