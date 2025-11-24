"""
schemas/user.py

Pydantic models for user request/response validation.
Provides data validation and serialization for authentication and user management.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, max_length=255, description="User password (min 8 chars)")
    email: Optional[EmailStr] = Field(None, description="User email address")
    
    @validator("username")
    def username_alphanumeric(cls, v):
        """Validate username contains only alphanumeric and underscores."""
        if not all(c.isalnum() or c == "_" for c in v):
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    email: Optional[EmailStr] = None
    email_reminders_enabled: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response in API."""
    id: str
    username: str
    email: Optional[str]
    email_reminders_enabled: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True  # Allow ORM model conversion


class UserWithToken(BaseModel):
    """Schema for user response with JWT token."""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
