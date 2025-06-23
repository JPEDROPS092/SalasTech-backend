"""
Simplified password hashing using bcrypt only
"""
import bcrypt
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PasswordManager:
    """Unified password management using bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt with automatic salt generation
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise ValueError("Failed to hash password")
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            hashed: Hashed password from database
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed.encode('utf-8')
            )
        except Exception as e:
            logger.warning(f"Error verifying password: {e}")
            return False
    
    @staticmethod
    def generate_random_hash() -> str:
        """
        Generate a random hash for tokens/identifiers
        
        Returns:
            str: Random hash
        """
        import secrets
        import time
        
        # Generate random bytes with timestamp
        random_data = f"{time.time()}{secrets.token_hex(16)}"
        return PasswordManager.hash_password(random_data)
