# raiz/database/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Esquemas de Usuário
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True