from pydantic import BaseModel, Field, EmailStr


class ChatCreate(BaseModel):
    user_id: int = Field(ge=0)


class UserEmail(BaseModel):
    user_email: EmailStr
