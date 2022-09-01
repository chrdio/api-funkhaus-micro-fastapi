import json
import uvicorn
from microfunkhaus import APP

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    PORT = config["port"]
    HOST = config["host"]
    KEYFILE = config["keyfile"]
    CERTFILE = config["certfile"]

uvicorn.run(
    APP,
    host=HOST,
    port=PORT,
    ssl_keyfile=KEYFILE,
    ssl_certfile=CERTFILE,
    )