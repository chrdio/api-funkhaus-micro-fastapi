from typing import Sequence
from API import (
    get_req_progression_generation,
    get_req_voices_generation,
    post_multi_requests,
    post_single_request,
    Performance,
    Progression,
    PseudoMIDI
)


async def generate_progression(performance: Performance):
    progression_raw = await post_single_request(*get_req_progression_generation(performance)) # type: str
    progression = Progression.parse_raw(progression_raw)
    voices_raw = await post_single_request(*get_req_voices_generation(performance, progression=progression)) # type: str
    voices = PseudoMIDI.parse_raw(voices_raw)
    return voices

