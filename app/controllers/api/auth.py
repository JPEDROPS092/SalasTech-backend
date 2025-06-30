"""
Authentication endpoints for React SPA
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Dict, Any
import logging

from ...core.security.auth import JWTManager
from ...core.security.password import PasswordManager
from ...core.security.middleware import get_current_user
from ...core.dependencies import get_user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth")


# Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    user_service = Depends(get_user_service)
):
    """
    Authenticate user and return JWT tokens
    
    Args:
        credentials: User email and password
        user_service: User service dependency
        
    Returns:
        TokenResponse: Access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Get user by email
        user = user_service.obter_por_email(credentials.email)
        if not user:
            logger.warning(f"Login attempt with non-existent email: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not PasswordManager.verify_password(credentials.password, user.senha):
            logger.warning(f"Failed login attempt for user: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create JWT tokens
        tokens = JWTManager.create_tokens(
            user_id=str(user.id),
            user_role=user.papel.value
        )
        
        logger.info(f"User successfully logged in: {credentials.email}")
        return TokenResponse(**tokens)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Login error for {credentials.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token using refresh token
    
    Args:
        request: Refresh token request
        
    Returns:
        TokenResponse: New access and refresh tokens
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        # Refresh tokens
        tokens = JWTManager.refresh_access_token(request.refresh_token)
        if not tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        logger.info("Token refreshed successfully")
        return TokenResponse(**tokens)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout user (client-side token invalidation)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Success message
    """
    logger.info(f"User logged out: {current_user.get('email')}")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserProfileResponse)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user profile
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserProfileResponse: User profile information
    """
    return UserProfileResponse(
        id=current_user["user_id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"]
    )


@router.get("/verify")
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Verify if current token is valid
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Token validity status
    """
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "role": current_user["role"]
    }