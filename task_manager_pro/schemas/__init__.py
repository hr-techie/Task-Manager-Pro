"""
schemas/__init__.py

Pydantic schema exports for request/response validation.
"""

from task_manager_pro.schemas.user import (
    UserRegister,
    UserLogin,
    UserUpdate,
    UserResponse,
    UserWithToken,
)

from task_manager_pro.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskPriority,
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "UserWithToken",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "TaskPriority",
]
