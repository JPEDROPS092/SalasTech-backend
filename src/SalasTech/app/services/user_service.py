import secrets
import string
import logging
from datetime import datetime, timedelta, timezone
from random import randint

from SalasTech.app.models import db
from SalasTech.app.models import dto
from SalasTech.app.models import enums
from SalasTech.app.repos import user_repo

from SalasTech.app.core.security import bcrypt_hashing
from SalasTech.app.core.security import jwt
from SalasTech.app.utils import formatting
from SalasTech.app.mappers import user_mapper
from SalasTech.app.exceptions.scheme import AppException

# Set up logging
logger = logging.getLogger(__name__)

# For legacy support
MIN_PASS = 100000
MAX_PASS = 999999

# Store password reset tokens (in a real app, this would be in a database)
# Format: {"token": {"user_id": id, "expires": datetime}}
PASSWORD_RESET_TOKENS = {}


def get_all(limit: int = 1000, offset: int = 0) -> list[dto.UserDTO]:
    return [user_mapper.db_to_get_dto(user) for user in user_repo.get(limit, offset)]


def get_by_id(id: int) -> db.UserDb:
    user = user_repo.get_by_id(id)
    if user is None:
        raise AppException(message="User not found", status_code=404)

    return user


def get_by_id_dto(id: int) -> dto.UserDTO:
    user = get_by_id(id)
    return user_mapper.db_to_get_dto(user)


def get_by_email(email: str) -> db.UserDb:
    email_form = formatting.format_string(email)
    user = user_repo.get_by_email(email_form)
    if user is None:
        raise AppException(message="User not found", status_code=404)

    return user


def get_by_email_dto(email: str) -> dto.UserDTO:
    user = get_by_email(email)
    return user_mapper.db_to_get_dto(user)


def create_user(obj: dto.UserCreateDTO) -> dto.UserDTO:
    user = _create(obj, enums.UserRole.USER)
    return user_mapper.db_to_get_dto(user)


def create_admin(obj: dto.UserCreateDTO) -> dto.UserDTO:
    user = _create(obj, enums.UserRole.ADMIN)
    return user_mapper.db_to_get_dto(user)


def update_name(user: db.UserDb, obj: dto.UserUpdateNameDTO) -> None:
    user.name = formatting.format_string(obj.name)
    user.surname = formatting.format_string(obj.surname)
    user_repo.update(user)


def update_password(user: dto.UserDTO, obj: dto.UserUpdatePassDTO) -> None:
    user_db = get_by_id(user.id)
    if bcrypt_hashing.validate(obj.old_password, user_db.password) is False:
        raise AppException(message="Incorrect password", status_code=422)

    _update_password(user_db, obj.new_password)


def reset_password(email: str) -> str:
    """Generate a password reset token and send reset instructions
    
    In a production environment, this would send an email with a reset link.
    For now, it returns the token that would be sent in the email.
    
    Args:
        email: User's email address
        
    Returns:
        str: Password reset token (for testing purposes)
        
    Raises:
        AppException: If user not found
    """
    try:
        user = get_by_email(email)
        
        # Generate a secure random token
        token = secrets.token_urlsafe(32)
        
        # Set token expiration (1 hour from now)
        expiration = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Store token with user ID and expiration
        PASSWORD_RESET_TOKENS[token] = {
            "user_id": user.id,
            "expires": expiration
        }
        
        # In a real application, send an email with a reset link
        reset_link = f"/auth/password/reset/{token}"
        
        logger.info(f"Password reset requested for {email}. Token: {token}")
        
        # Return the token for testing purposes
        # In production, this would return None and send an email
        return token
    except Exception as e:
        logger.error(f"Password reset error for {email}: {str(e)}")
        # Don't expose whether the email exists or not
        raise AppException("If the email exists, a password reset link will be sent.", 200)


def delete(id: int) -> None:
    user_repo.delete(id)


def _create(obj: dto.UserCreateDTO, role: enums.UserRole) -> db.UserDb:
    name_formatted = formatting.format_string(obj.name)
    surname_formatted = formatting.format_string(obj.surname)
    email_formatted = formatting.format_string(obj.email)

    if name_formatted == "":
        raise AppException(message="Name is not valid", status_code=422)

    if surname_formatted == "":
        raise AppException(message="Surname is not valid", status_code=422)

    if email_formatted == "":
        raise AppException(message="Email is not valid", status_code=422)

    if user_repo.get_by_email(email_formatted) is not None:
        raise AppException(message="Email already exists", status_code=422)

    user_to_db = db.UserDb()
    user_to_db.name = name_formatted
    user_to_db.surname = surname_formatted
    user_to_db.role = role
    user_to_db.email = email_formatted
    user_to_db.password = bcrypt_hashing.hash(obj.password)

    return user_repo.add(user_to_db)


def _update_password(user: db.UserDb, new_password: str) -> None:
    """Update user's password with proper hashing
    
    Args:
        user: User database object
        new_password: New password (plain text)
    """
    # Validate password strength
    if len(new_password) < 8:
        raise AppException("Password must be at least 8 characters long", 400)
        
    # Hash the new password
    new_pass_hash = bcrypt_hashing.hash(new_password)
    user.password = new_pass_hash
    user_repo.update(user)


def confirm_reset_password(token: str, new_password: str) -> bool:
    """Confirm password reset with token and set new password
    
    Args:
        token: Password reset token
        new_password: New password to set
        
    Returns:
        bool: True if password was reset successfully
        
    Raises:
        AppException: If token is invalid or expired
    """
    # Check if token exists
    if token not in PASSWORD_RESET_TOKENS:
        logger.warning(f"Invalid password reset token attempted: {token}")
        raise AppException("Invalid or expired reset token", 400)
    
    # Get token data
    token_data = PASSWORD_RESET_TOKENS[token]
    
    # Check if token is expired
    if token_data["expires"] < datetime.now(timezone.utc):
        # Remove expired token
        del PASSWORD_RESET_TOKENS[token]
        logger.warning(f"Expired password reset token attempted: {token}")
        raise AppException("Invalid or expired reset token", 400)
    
    try:
        # Get user and update password
        user = get_by_id(token_data["user_id"])
        _update_password(user, new_password)
        
        # Remove used token
        del PASSWORD_RESET_TOKENS[token]
        
        logger.info(f"Password reset successful for user ID: {user.id}")
        return True
    except Exception as e:
        logger.error(f"Error during password reset confirmation: {str(e)}")
        raise AppException("Password reset failed", 500)


def _reset_password(user: db.UserDb) -> str:
    """Legacy password reset function - generates a random password
    
    This is kept for backward compatibility but should be deprecated.
    
    Args:
        user: User database object
        
    Returns:
        str: New random password
    """
    new_password = str(randint(MIN_PASS, MAX_PASS))
    _update_password(user, new_password)

    return new_password
