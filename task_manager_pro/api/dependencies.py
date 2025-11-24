"""
api/dependencies.py

FastAPI dependency injections for JWT authentication and database access.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from task_manager_pro.utils.security import decode_token
from task_manager_pro.storage.sql_storage import SQLStorage

security = HTTPBearer()
storage = SQLStorage()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token from request header
        
    Returns:
        str: User ID from token
        
    Raises:
        HTTPException: 401 if token invalid or expired
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


async def get_storage() -> SQLStorage:
    """
    Dependency to provide SQLStorage instance.
    
    Yields:
        SQLStorage: Database storage instance
    """
    return storage
