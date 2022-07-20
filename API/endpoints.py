from pydantic import BaseModel

class Endpoint(BaseModel):
    name: str
    host: str
    port: str
    path: str
    prefix: str = 'http://'

    def __str__(self):
        return f"{self.prefix}{self.host}:{self.port}/{self.path}"