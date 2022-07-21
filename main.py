import json
from typing import Union
from fastapi import FastAPI
from aiohttp import ClientSession
from API.outer_models import PerformanceResponse
from actions import generate_progression
from API import PerformanceRequest
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


@app.post("/progression")
async def gen_progression(performance: PerformanceRequest):
    responses = await generate_progression(performance)
    return responses


if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)