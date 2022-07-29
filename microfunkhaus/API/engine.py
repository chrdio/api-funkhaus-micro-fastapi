import asyncio
import json
from typing import Any, Optional, Tuple
from aiohttp import ClientSession
from pydantic import BaseModel
from .endpoints import Endpoint

async def post_single_request(endpoint: Endpoint, payload: BaseModel, *, session: ClientSession):
    serializable = json.loads(payload.json())
    async with session.post(str(endpoint), json=serializable, raise_for_status=True) as response:
        return await response.text()

async def post_multi_requests(*items: Tuple[Endpoint, BaseModel], session: ClientSession):
    async with session:
        results = asyncio.gather(
            *[post_single_request(endpoint, payload, session=session) for endpoint, payload in items]
        )
        return await results

def instant_fire_coroutines(*coroutines) -> Tuple[asyncio.Task]:

    # return tuple(storage.add(asyncio.create_task(coro)) for coro in coroutines)
    return tuple(asyncio.create_task(coro) for coro in coroutines)