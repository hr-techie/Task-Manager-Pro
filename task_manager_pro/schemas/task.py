"""
schemas/task.py

Pydantic models for task request/response validation.
Provides data validation and serialization for API and CLI usage.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    due_date: str = Field(..., description="Due date in YYYY-MM-DD format")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    
    @validator("due_date")
    def validate_due_date(cls, v):
        """Validate due date format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("due_date must be in YYYY-MM-DD format")
        return v


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")
    priority: Optional[TaskPriority] = None
    completed: Optional[bool] = None
    
    @validator("due_date")
    def validate_due_date(cls, v):
        """Validate due date format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("due_date must be in YYYY-MM-DD format")
        return v


class TaskResponse(BaseModel):
    """Schema for task response in API/CLI."""
    id: str
    title: str
    description: Optional[str]
    due_date: str
    priority: TaskPriority
    completed: bool
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    
    class Config:
        from_attributes = True  # Allow ORM model conversion


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""
    total: int
    tasks: list[TaskResponse]
    page: int
    page_size: int
