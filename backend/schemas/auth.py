from pydantic import BaseModel, EmailStr, field_validator, model_validator
from models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    name: str | None = None
    role: UserRole = UserRole.ta

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value):
        if isinstance(value, str):
            roles = {
                "PROFESSOR": UserRole.instructor,
                "INSTRUCTOR": UserRole.instructor,
                "TA": UserRole.ta,
            }
            return roles.get(value.upper(), value.lower())
        return value

    @model_validator(mode="after")
    def normalize_name(self):
        self.full_name = self.full_name or self.name
        if not self.full_name:
            raise ValueError("Full name is required")
        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole

    model_config = {"from_attributes": True}
