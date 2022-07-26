from email import generator
import json
from fastapi import (
    FastAPI,
    Response,
    HTTPException,
    Body,
    Query,
    Header,
    status,
    Request,
    Depends,
    Path,
)
from API import (
    PerformanceRequest,
    LabelingRequest,
    AmendmentRequest,
    GenericRequest,
    PerformanceResponse,
)

from aiohttp import ClientResponseError
from actions import generate_progression, send_labels, amend_progression, create_user
app = FastAPI(
    title="microfunkhaus",
    docs_url='/'
    )

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    TITLE = config["title"]
    PORT = config["port"]
    HOST = config["host"]
    RELOAD = config["reload"]

generator_summary = """You can specify the optional key and mode (graph) parameters,
or even supply the otherwise verbatim progression with a changed key to transpose it."""
@app.post(
    "/generate",
    description="Generates a new progression",
    summary=generator_summary,
    response_description="The generated progression",
    response_model=PerformanceResponse,
    status_code=status.HTTP_200_OK,
    )
async def gen_progression(
    performance: PerformanceRequest
    ):
    try:
        responses = await generate_progression(performance)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    return responses

@app.post("/amend/{index}")
async def amend_performance(
    full_request: AmendmentRequest,
    index: int = Path(
        ...,
        title="Index",
        description="The chord under this index will be substituted",
        example=1,
        )
    ):
    try:
        responses = await amend_progression(full_request, index)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    return responses


@app.post("/label")
async def label_progression(labeling_request: LabelingRequest):
    try:
        responses = await send_labels(labeling_request)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    return Response(status_code=201)

@app.post("/create_user_id")
async def initialize_user(request: GenericRequest):
    try:
        user_obj = await create_user(request)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    return Response(content=user_obj.json(), status_code=201, media_type="application/json")


if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)