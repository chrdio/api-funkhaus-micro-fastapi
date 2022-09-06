import json
import uvicorn

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    PORT = config["port"]
    HOST = config["host"]
    KEYFILE = config["keyfile"]
    CERTFILE = config["certfile"]
    RELOAD = config["reload"]

from microfunkhaus import APP

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
