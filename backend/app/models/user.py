from pydantic import BaseModel

class User(BaseModel):
    id: str
    email: str
    name: str | None = None
    provider: str | None = "firebase"
