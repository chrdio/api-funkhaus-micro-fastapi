import asyncio
from typing import Optional, Tuple
from aiohttp import ClientSession
from pydantic import BaseModel
from .endpoints import Endpoint

async def post_single_request(endpoint: Endpoint, payload: BaseModel, session: Optional[ClientSession] = None) -> str:
    if session is None:
        async with ClientSession() as session:
            return await post_single_request(endpoint, payload, session=session)
    else:
        async with session.post(str(endpoint), json=payload.dict()) as response:
            raw = await response.text()
            if response.status != 200:
                print(raw)
            return raw

async def post_multi_requests(*items: Tuple[Endpoint, BaseModel]):
    # classes = (item[1].__class__ for item in items)
    async with ClientSession() as session:
        results = asyncio.gather(
            *[post_single_request(endpoint, payload, session=session) for endpoint, payload in items]
        )
        return await results # type: List[str]