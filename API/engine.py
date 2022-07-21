import asyncio
from typing import Tuple
from aiohttp import ClientSession
from pydantic import BaseModel
from .endpoints import Endpoint

async def post_single_request(endpoint: Endpoint, payload: BaseModel, session: ClientSession):
    async with session.post(str(endpoint), json=payload.dict()) as response:
        return response.status, await response.json() # type: override -> Tuple[int, str]

async def post_multi_requests(*items: Tuple[Endpoint, BaseModel]):
    # classes = (item[1].__class__ for item in items)
    async with ClientSession() as session:
        results = asyncio.gather(
            *[post_single_request(endpoint, payload, session) for endpoint, payload in items]
        )
        return await results # type: override -> Sequence[Tuple[int, str]]