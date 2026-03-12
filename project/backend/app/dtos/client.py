from pydantic import BaseModel, Field


class ClientResponse(BaseModel):
    id: int = Field(..., description='Название сделки')
    name: str = Field(..., min_length=1, max_length=255, description='Название сделки')
