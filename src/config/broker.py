from pydantic import BaseModel


class BrokerConfig(BaseModel):
    url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/0"
