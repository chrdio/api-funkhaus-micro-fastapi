from fastapi import FastAPI
from aiohttp import ClientSession
from API import SessionData, Endpoint, post_single_request, post_multi_requests
from API.inner_models import Progression, ProgressionRequest
app = FastAPI()

chrdio_api = Endpoint(
    name="random_performance",
    host="127.0.0.1",
    port="8001",
    path="generate/4",
)
req_dict = {
    "graph": "master_graph"
}


req = ProgressionRequest.parse_obj(req_dict)
@app.get("/")
async def test():
    responses = await post_multi_requests(*[(chrdio_api, req) for n in range(1000)])
    return responses