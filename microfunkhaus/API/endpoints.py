import json
from typing import Optional
from pydantic import BaseModel

class Endpoint(BaseModel):
    name: str
    host: str
    port: str
    path: str
    option: Optional[str] = None
    prefix: str = 'http://'

    def __str__(self):
        if self.option is not None:
            option = '/' + self.option
        else:
            option = ''
        return f"{self.prefix}{self.host}:{self.port}/{self.path}{option}"

with open('.endpoints.json', 'r') as endpoints_file:
    endpoints = json.load(endpoints_file)
    ENDPOINTS = {endpoint['name']: Endpoint(**endpoint) for endpoint in endpoints}
