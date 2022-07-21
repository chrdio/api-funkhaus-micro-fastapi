import json
from typing import Optional
from pydantic import BaseModel

class Endpoint(BaseModel):
    name: str
    host: str
    port: str
    path: str
    option: Optional[str] = ""
    prefix: str = 'http://'

    def __str__(self):
        return f"{self.prefix}{self.host}:{self.port}/{self.path}/{self.option}"

with open('.endpoints.json', 'r') as endpoints_file:
    endpoints = json.load(endpoints_file)
    ENDPOINTS = {endpoint['name']: Endpoint(**endpoint) for endpoint in endpoints}
