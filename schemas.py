from pydantic import BaseModel, ConfigDict, Field

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    role: str = "student"

class LoginIn(BaseModel):
    email: str
    password: str

class CategoryIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    filename: str
    category_id: int | None
    uploader_id: int
    is_approved: bool
