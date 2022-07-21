import json
from typing import Dict, Sequence
from API import (
    get_req_progression_generation,
    get_req_voices_generation,
    get_req_midihex_generation,
    post_multi_requests,
    construct_performance,
    construct_progression,
    post_single_request,
    Performance,
    Progression,
    PseudoMIDI
)
from API.outer_models import PerformanceResponse


async def generate_progression(performance: Performance) -> PerformanceResponse:
    if isinstance(performance, PerformanceResponse):
        progression = construct_progression(performance)
    else:
        req_prog = get_req_progression_generation(performance)
        progression_raw = await post_single_request(*req_prog) # type: str
        progression = Progression.parse_raw(progression_raw)
        

    req_voice = get_req_voices_generation(performance, progression=progression)
    voices_raw = await post_single_request(*req_voice) # type: str
    voices = PseudoMIDI.parse_raw(voices_raw)

    req_midihex = get_req_midihex_generation(voices)
    midihex_raw = await post_single_request(*req_midihex) # type: str
    midihex = json.loads(midihex_raw)

    cheetsheet = req_voice[1]
    outcoming_performance = construct_performance(
        progression,
        cheetsheet,
        midihex
    )

    return outcoming_performance

