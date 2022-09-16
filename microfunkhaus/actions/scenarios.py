import json
import asyncio
from typing import Sequence
from aiohttp import ClientSession, ClientResponseError
from chrdiotypes.musical import PseudoMIDI, ProgressionFields

from ..API import (
    get_req_progression_generation,
    get_req_progression_amendment,
    get_req_voices_generation,
    submit_data_tasks,
    PerformanceRequest,
    AmendmentRequest,
    LabelingRequest,
    PerformanceResponse,
    construct_performance,
    construct_progression,
    construct_session_data,
    construct_user_data,
    construct_label_data,
    post_single_request,
    get_req_midihex_generation,
    ping_dependency,
    Endpoint,
)



async def generate_progression(full_request: PerformanceRequest) -> PerformanceResponse:
    """Makes calls to
    the 'micropathforger',
    the 'microvoicemaster' &
    the 'microbureaucrat' services
    to generate a chord progression
    and create its performance.
     
    Sends user data to the 'microaccountant'.
    """

    # Define a set instead of a variable
    # in case there will be more requests
    # of this type
    task_chest = set()
    local_session = ClientSession()
    performance = full_request.performance_object

    # Send user data
    if full_request.user_object is not None:
        session_data = construct_user_data(full_request)
    else:
        session_data = construct_session_data(full_request)
    submit_data_tasks(session_data, storage=task_chest, session=local_session)

    # Either generates or parses a chord progression.
    try:
        progression = construct_progression(performance)  # type: ignore PerformanceResponse
    except AttributeError:
        req_prog = get_req_progression_generation(performance)
        progression_raw = await post_single_request(*req_prog, session=local_session)
        progression = ProgressionFields.parse_raw(progression_raw)

    # Generates voices
    req_voice = get_req_voices_generation(performance, progression=progression)
    voices_raw = await post_single_request(*req_voice, session=local_session)
    voices = PseudoMIDI.parse_raw(voices_raw)
    cheetsheet = req_voice[1]

    # Generate a midifile
    req_midihex = get_req_midihex_generation(voices)
    midihex_raw = await post_single_request(*req_midihex, session=local_session)
    midihex = json.loads(midihex_raw)

    # Assembles a performance
    outcoming_performance = construct_performance(
        progression=progression,
        cheet_sheet=cheetsheet,
        hex_blob=midihex,
        pseudo_midi=voices,
    )

    # Deals with background processes
    try:
        await asyncio.gather(*task_chest)
    except ClientResponseError as e:  # pragma: no cover (no way to test remotely)
        raise
    await local_session.close()
    del task_chest

    return outcoming_performance


async def amend_progression(
    full_request: AmendmentRequest, index: int
    ) -> PerformanceResponse:
    """Makes calls to
    the 'micropathforger',
    the 'microvoicemaster' &
    the 'microbureaucrat' services
    to amend a chord progression
    and create its performance.
     
    Sends user data to the 'microaccountant'.
    """

    # Define a set instead of a variable
    # in case there will be more requests
    # of this type
    task_chest = set()
    old_performance = full_request.performance_object
    local_session = ClientSession()

    # Send user data
    if full_request.user_object is not None:
        session_data = construct_user_data(full_request)
    else:
        session_data = construct_session_data(full_request)
    submit_data_tasks(session_data, storage=task_chest, session=local_session)

    # Generates an amended progression.
    req_amend_progression = get_req_progression_amendment(old_performance, index)
    new_progression_raw = await post_single_request(
        *req_amend_progression, session=local_session
    )
    new_progression = ProgressionFields.parse_raw(new_progression_raw)

    # Generates voices
    req_voice = get_req_voices_generation(old_performance, progression=new_progression)
    voices_raw = await post_single_request(*req_voice, session=local_session)
    voices = PseudoMIDI.parse_raw(voices_raw)
    cheetsheet = req_voice[1]

    # Generates a midifile
    req_midihex = get_req_midihex_generation(voices)
    midihex_raw = await post_single_request(*req_midihex, session=local_session)
    midihex = json.loads(midihex_raw)

    # Assembles a performance
    outcoming_performance = construct_performance(
        progression=new_progression,
        cheet_sheet=cheetsheet,
        hex_blob=midihex,
        pseudo_midi=voices,
    )

    # Deals with background processes
    try:
        await asyncio.gather(*task_chest)
    except ClientResponseError as e:  # pragma: no cover (no way to test remotely)
        raise
    await local_session.close()
    del task_chest
    return outcoming_performance


async def send_labels(labeling_request: LabelingRequest) -> bool:
    """Notifies the 'microaccountant' about the user and a new label"""
    
    # Define a set instead of a variable
    # in case there will be more requests
    # of this type
    task_chest = set()
    local_session = ClientSession()

    if labeling_request.user_object is not None:
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


async def healthcheck_dependencies(deps: Sequence[Endpoint]) -> bool:
    """Checks if all services are online"""

    session = ClientSession()
    async with session:
        oks = await asyncio.gather(*(ping_dependency(e, session=session) for e in deps))
    return all(oks)
