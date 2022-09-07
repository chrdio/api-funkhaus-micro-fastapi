import json
import sys
import uvicorn
from typing import Set
from pydantic import BaseModel
from microfunkhaus import generate_app_with_config

class ValidTokens(BaseModel):
    __root__: Set[str]

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    PORT = config["port"]
    HOST = config["host"]
    KEYFILE = config["keyfile"]
    CERTFILE = config["certfile"]
    RELOAD = config["reload"]
try:
    valid_tokens = ValidTokens.parse_raw(sys.argv[1])
except:
    raise ValueError("Please, provide valid JSON-encoded tokens.")

APP = generate_app_with_config(tokens=valid_tokens.__root__, remote_healthcheck_on_startup=False)

if __name__ == "__main__":
    uvicorn.run(
        "main:APP",
        host=HOST,
        port=PORT,
        debug=True,
        reload=RELOAD,
        ssl_keyfile=KEYFILE,
        ssl_certfile=CERTFILE,
    )
