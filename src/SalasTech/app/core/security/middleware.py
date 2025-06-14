"""
Simplified authentication middleware for React SPA
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging

from .auth import JWTManager
from ..dependencies import get_user_service
from ...models.enums import UserRole

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_service = Depends(get_user_service)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from Bearer token
    
    Args:
        credentials: HTTP Authorization header with Bearer token
        user_service: User service dependency
        
    Returns:
        dict: User information
        
    Raises:
        HTTPException: If token is missing, invalid, or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify access token
    payload = JWTManager.verify_token(credentials.credentials, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user exists in database
    try:
        user = user_service.obter_por_id(int(user_id))
        if not user:
            logger.warning(f"User not found for token: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.papel.value,
            "name": f"{user.nome} {user.sobrenome}",
            "user_object": user  # Full user object for backward compatibility
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to verify user has admin role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Admin user information
        
    Raises:
        HTTPException: If user is not an admin
    """
    user_role = current_user.get("role")
    
    if user_role != UserRole.ADMIN.value:
        logger.warning(f"Non-admin access attempt by user: {current_user.get('user_id')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_service = Depends(get_user_service)
) -> Optional[Dict[str, Any]]:
    """
    Dependency to get current user if token is provided (optional auth)
    
    Args:
        credentials: HTTP Authorization header with Bearer token
        user_service: User service dependency
        
    Returns:
        dict: User information if authenticated, None if not
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, user_service)
    except HTTPException:
        # Return None for optional authentication
        return None
