from pydantic import BaseModel

class UsuarioR(BaseModel):
    usu_id: int
    nombres: str
    email: str
    usu_key_access: str

class LoginR(BaseModel):
    usu_id: int
    usu_key_access: str
    cia_id: int
    per_nombre: str
    cia_nombre: str

class LoginForm(BaseModel):
    email: str | None = None
    password: str | None = None