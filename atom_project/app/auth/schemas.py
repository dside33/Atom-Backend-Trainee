from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr


class UserCreate(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=4)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
