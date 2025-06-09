from datetime import datetime
from datetime import timezone
import logging

from fastapi import Request
from fastapi import Response
from fastapi import Depends

from salstech.app.core.config import CONFIG
from salstech.app.services import user_service
from salstech.app.exceptions.scheme import AppException
from salstech.app.models import enums
from salstech.app.models import dto
from salstech.app.core.security import jwt
from salstech.app.core.security import bcrypt_hashing

# Set up logging
logger = logging.getLogger(__name__)


def get_token(req: Request, res: Response) -> dto.Token:
    """Get and validate token from cookies
    
    Raises:
        AppException: If token is missing, expired or invalid
        
    Returns:
        dto.Token: Valid token object
    """
    session_token = req.cookies.get(CONFIG.COOKIES_KEY_NAME)
    if session_token is None:
        logger.warning("No session token found in cookies")
        raise AppException(status_code=401, message="Unauthorized: No session token")

    token_dict = jwt.decode(session_token)
    if token_dict is None:
        logger.warning("Invalid or expired token")
        # Clear invalid cookie
        res.delete_cookie(
            key=CONFIG.COOKIES_KEY_NAME,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        raise AppException(status_code=401, message="Unauthorized: Invalid or expired token")

    return dto.Token(**token_dict)

def get_user(req: Request, res: Response) -> dto.UserDTO:
    """Get user from token in cookies
    
    Raises:
        AppException: If user not found or token invalid
        
    Returns:
        dto.UserDTO: User data
    """
    token = get_token(req, res)

    try:
        user = user_service.get_by_id(token.user_id)
        if user is None:
            logger.warning(f"User not found for ID: {token.user_id}")
            res.delete_cookie(
                key=CONFIG.COOKIES_KEY_NAME,
                httponly=True,
                secure=True,
                samesite="lax"
            )
            raise AppException(status_code=401, message="Unauthorized: User not found")

        return user
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        res.delete_cookie(
            key=CONFIG.COOKIES_KEY_NAME,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        raise AppException(status_code=401, message="Unauthorized: Error retrieving user")

def get_admin(user: dto.UserDTO = Depends(get_user)) -> dto.UserDTO:
    """Check if user has admin role
    
    Args:
        user: User data from get_user dependency
        
    Raises:
        AppException: If user is not an admin
        
    Returns:
        dto.UserDTO: Admin user data
    """
    if user.role != enums.UserRole.ADMIN:
        logger.warning(f"Non-admin access attempt by user ID: {user.id}")
        raise AppException(status_code=403, message="Forbidden: Admin access required")

    return user

async def login(obj: dto.UserLoginDTO, res: Response) -> str:
    """Authenticate user and set session cookie
    
    Args:
        obj: Login credentials
        res: Response object to set cookie
        
    Raises:
        AppException: If credentials are invalid
        
    Returns:
        str: JWT token string
    """
    NOW = datetime.now(timezone.utc)

    try:
        user_db = user_service.get_by_email(obj.email)
        # Remove debug print statement
        if bcrypt_hashing.validate(obj.password, user_db.password) is False:
            logger.warning(f"Failed login attempt for email: {obj.email}")
            raise AppException("Incorrect email or password", 401)

        # Set expiration date for token
        exp_date = NOW + CONFIG.SESSION_TIME
        
        # Create token with user data
        token = dto.Token(user_id=user_db.id, role=user_db.role)
        token_str = jwt.encode(token.model_dump(), exp_date)

        # Set secure cookie
        res.set_cookie(
            key=CONFIG.COOKIES_KEY_NAME,
            value=token_str,
            expires=exp_date,
            httponly=True,  # Prevent JavaScript access
            secure=True,    # HTTPS only
            samesite="lax"  # CSRF protection
        )
        
        logger.info(f"User logged in: {obj.email}")
        return token_str
    except AppException:
        # Re-raise application exceptions
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise AppException("Authentication failed", 401)

async def logout(res: Response) -> None:
    """Clear session cookie
    
    Args:
        res: Response object to clear cookie
    """
    res.delete_cookie(
        key=CONFIG.COOKIES_KEY_NAME,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    logger.info("User logged out")