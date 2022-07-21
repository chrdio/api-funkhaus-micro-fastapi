from typing import Sequence
from API import (
    get_req_progression_generation,
    post_multi_requests,
    Performance
)


async def generate_progression(performance: Performance):
    return await post_multi_requests(get_req_progression_generation(performance))
