from typing import List
from pydantic import BaseModel
from .search_result_item import SearchResultItem


class SearchResult(BaseModel):
    data: List[SearchResultItem]
