from pydantic import BaseModel

class Usuario(BaseModel):
    usu_id: int | None = None
    user: str
    email: str
    password: str