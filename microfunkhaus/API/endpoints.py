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
    
    def __hash__(self):
        return hash(tuple(self.dict().values()))

with open('.endpoints.json', 'r') as endpoints_file:
    endpoints = json.load(endpoints_file)
    ENDPOINTS = {endpoint['name']: Endpoint(**endpoint) for endpoint in endpoints}
    for e in endpoints:
        e['path'] = "healthcheck"
        e['name'] = str(e)
        e['option'] = None
    HEALTHPOINTS = list(set(Endpoint(**e) for e in endpoints))