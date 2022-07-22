import asyncio
import json
from typing import Optional, Tuple
from aiohttp import ClientSession
from pydantic import BaseModel
from .endpoints import Endpoint

async def post_single_request(endpoint: Endpoint, payload: BaseModel, *, session: ClientSession):
    serializable = json.loads(payload.json())
    async with session.post(str(endpoint), json=serializable, raise_for_status=True) as response:
        return response.text()

async def post_multi_requests(*items: Tuple[Endpoint, BaseModel], session: ClientSession):
    async with session:
        results = asyncio.gather(
            *[post_single_request(endpoint, payload, session=session) for endpoint, payload in items]
        )
        return results

async def instant_fire_coroutines(*coroutines, storage: set) -> Tuple[asyncio.Task]:
    
    def store_task(task: asyncio.Task, storage: set):
        storage.add(task)
        return task

    return tuple(store_task(asyncio.create_task(coro), storage) for coro in coroutines)
