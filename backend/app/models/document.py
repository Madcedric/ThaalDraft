from pydantic import BaseModel
from typing import List, Dict, Any

class Section(BaseModel):
    heading: str
    content: str

class DocumentResponse(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    sections: List[Section]
    references: List[str]
    tables: List[List[List[str]]]
    figures: List[str]
