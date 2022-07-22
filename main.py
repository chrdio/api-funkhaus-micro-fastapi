import json
from fastapi import FastAPI, Response, HTTPException
from API import PerformanceRequest, LabelingRequest
from API.outer_models import AmendmentRequest, GenericRequest
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


@app.post("/generate")
async def gen_progression(performance: PerformanceRequest):
    responses = await generate_progression(performance)
    return responses

@app.post("/amend/{index}")
async def amend_performance(full_request: AmendmentRequest, index: int):
    responses = await amend_progression(full_request, index)
    return responses


@app.post("/label")
async def label_progression(labeling_request: LabelingRequest):
    labels_sent = await send_labels(labeling_request)
    if labels_sent:
        return Response(status_code=201)
    else:
        raise HTTPException(status_code=400, detail="Labeling failed")

@app.post("/create_user_id")
async def initialize_user(request: GenericRequest):
    user_obj = await create_user(request)
    user_obj = user_obj.json()
    return Response(content=user_obj, status_code=201, media_type="application/json")


if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)