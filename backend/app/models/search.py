from pydantic import BaseModel

from app.models.listing import Listing


class SearchResponse(BaseModel):
    query: str
    results: list[Listing]
