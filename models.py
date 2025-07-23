from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Name must be at least 2 characters")
    email: EmailStr = Field(..., description="Invalid email format")
    mobile_number: str = Field(..., description="Mobile number must be 10 digits")
    age: int = Field(..., ge=1, le=120, description="Age must be between 1 and 120")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    confirm_password: str

    @validator("name")
    def validate_name(cls, v):
        if not v.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabets and spaces")
        return v

    @validator("mobile_number")
    def validate_mobile(cls, v):
        if not v.isdigit():
            raise ValueError("Mobile number must contain only digits")
        if len(v) != 10:
            raise ValueError("Mobile number must be exactly 10 digits")
        return v


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Invalid email format")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")


class ResetPassword(BaseModel):
    email: EmailStr = Field(..., description="Invalid email format")
    new_password: str = Field(..., min_length=6, description="New password must be at least 6 characters")
    confirm_password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    mobile_number: str
    age: int
