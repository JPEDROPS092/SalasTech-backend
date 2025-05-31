from fastapi import APIRouter, Body, Path, Request, Depends
from fastapi import status
from fastapi import Response
import logging

from app.models import dto
from app.services import user_service
from app.core.security import session
from app.core.security import rate_limiter
from app.core.security import csrf
from app.core import dependencies
from app.exceptions.scheme import AppException

# Configure logger
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=dto.UserDTO)
async def register(user: dto.UserCreateDTO, request: Request):
    # Apply rate limiting to registration to prevent abuse
    rate_limiter.check_login_rate_limit(request)
    
    # Log registration attempt
    logger.info(f"Registration attempt for email: {user.email}")
    
    return user_service.create_user(user)

@router.post("/login", status_code=status.HTTP_200_OK, response_model=str)
async def login(obj: dto.UserLoginDTO, res: Response, request: Request):
    # Apply rate limiting to login attempts
    rate_limiter.check_login_rate_limit(request)
    
    # Log login attempt (without password)
    logger.info(f"Login attempt for email: {obj.email}")
    
    return await session.login(obj, res)

@router.get("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(res: Response):
    await session.logout(res)

@router.get("/validate", response_model=dto.Token)
async def check_session(token: dependencies.token_dependency):
    return token

@router.put("/password/update", status_code=204)
def update_password(dto: dto.UserUpdatePassDTO, user: dependencies.user_dependency):
    user_service.update_password(user, dto)

@router.post("/password/reset", status_code=200, response_model=dict)
async def reset_password(request: Request, email: str = Body(..., embed=True)):
    """Request a password reset
    
    In production, this would send an email with a reset link.
    For development, it returns the token that would be sent.
    """
    # Apply rate limiting to password reset attempts
    rate_limiter.check_password_reset_rate_limit(request)
    
    # Log password reset attempt
    logger.info(f"Password reset attempt for email: {email}")
    
    token = user_service.reset_password(email)
    # In production, don't return the token, just a success message
    return {"message": "If the email exists, a password reset link will be sent.", "token": token}


@router.post("/password/reset/{token}", status_code=200)
async def confirm_reset_password(
    request: Request,
    token: str = Path(..., description="Password reset token"),
    password: str = Body(..., embed=True)
):
    """Confirm password reset with token and set new password"""
    # Apply rate limiting to password reset confirmation
    rate_limiter.check_password_reset_rate_limit(request)
    
    # Validate password strength
    if len(password) < 8:
        raise AppException("Password must be at least 8 characters long", 400)
    
    # Check for common password patterns
    common_passwords = ["password", "123456", "qwerty", "admin"]
    if any(common in password.lower() for common in common_passwords):
        raise AppException("Password is too common or easily guessable", 400)
    
    # Log password reset confirmation attempt (without showing the token or password)
    logger.info(f"Password reset confirmation attempt with token: {token[:5]}...")
    
    success = user_service.confirm_reset_password(token, password)
    if success:
        logger.info("Password reset successful")
        return {"message": "Password reset successful"}
    else:
        logger.warning("Password reset failed - invalid or expired token")
        raise AppException("Password reset failed - invalid or expired token", 400)