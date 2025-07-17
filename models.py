from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    mobile_number: str
    age: int
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str
    confirm_password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    mobile_number: str
    age: int
