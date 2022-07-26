import asyncio
from fastapi.encoders import jsonable_encoder
from typing import Tuple
from aiohttp import ClientSession
from pydantic import BaseModel
from .endpoints import Endpoint


async def post_single_request(
    endpoint: Endpoint, payload: BaseModel, *, session: ClientSession
    ) -> str:
    """Makes a single POST request according
    to the specified endpoint object
    and the pydantic-object payload.
    """

    serializable = jsonable_encoder(payload)
    async with session.post(
        str(endpoint), json=serializable, raise_for_status=True
    ) as response:
        return await response.text()


async def ping_dependency(endpoint: Endpoint, *, session: ClientSession) -> bool:
    """Returns True if endpoint responds OK (<400), else False"""

    async with session.get(str(endpoint), raise_for_status=True) as response:
        return response.ok


# A legacy multirequest sender
# async def post_multi_requests(*items: Tuple[Endpoint, BaseModel], session: ClientSession):
#     async with session:
#         results = asyncio.gather(
#             *[post_single_request(endpoint, payload, session=session) for endpoint, payload in items]
#         )
#         return await results


def instant_fire_coroutines(*coroutines) -> Tuple[asyncio.Task]:
    """Starts execution of coroutines immidiately.
    Returns a tuple of awaitable tasks.
    """

    return tuple(asyncio.create_task(coro) for coro in coroutines)
