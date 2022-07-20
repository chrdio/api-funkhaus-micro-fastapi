import asyncio
from typing import Tuple
from aiohttp import ClientSession
from pydantic import BaseModel

async def post_single_request(url: str, payload: BaseModel, session: ClientSession):
    async with session.post(url, json=payload) as response:
        return await response.json()

async def post_synchronous_requests(*items: Tuple[str, BaseModel]):
    # classes = (item[1].__class__ for item in items)
    async with ClientSession() as session:
        results = asyncio.gather(
            *[post_single_request(url, payload, session) for url, payload in items]
        )
        return await results