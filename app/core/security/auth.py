"""
JWT Authentication manager for React SPA
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
import logging
import os
from ..config import CONFIG

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET_KEY", CONFIG.HASH_SALT)
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


class JWTManager:
    """JWT token management for React authentication"""
    
    @staticmethod
    def create_tokens(user_id: str, user_role: str) -> Dict[str, Any]:
        """
        Create access and refresh tokens for user
        
        Args:
            user_id: User identifier
            user_role: User role (admin, user, etc.)
            
        Returns:
            dict: Contains access_token, refresh_token, expires_in
        """
        now = datetime.now(timezone.utc)
        
        # Access token payload (short-lived)
        access_payload = {
            "user_id": user_id,
            "role": user_role,
            "type": "access",
            "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": now,
            "sub": user_id  # Standard JWT subject claim
        }
        
        # Refresh token payload (long-lived)
        refresh_payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": now,
            "sub": user_id
        }
        
        try:
            access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
            }
        except Exception as e:
            logger.error(f"Error creating tokens: {e}")
            raise ValueError("Failed to create authentication tokens")
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            token_type: Expected token type ("access" or "refresh")
            
        Returns:
            dict: Token payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token, 
                JWT_SECRET, 
                algorithms=[JWT_ALGORITHM],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True
                }
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                logger.warning(f"Token type mismatch. Expected: {token_type}, Got: {payload.get('type')}")
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.info(f"Token expired: {token_type}")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {e}")
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Create new access token from valid refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            dict: New token pair or None if refresh token invalid
        """
        payload = JWTManager.verify_token(refresh_token, "refresh")
        if not payload:
            return None
            
        # Create new token pair (this also refreshes the refresh token)
        return JWTManager.create_tokens(
            user_id=payload["user_id"],
            user_role=payload.get("role", "user")  # Default role if missing
        )
    
    @staticmethod
    def decode_token_payload(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without verification (for debugging)
        
        Args:
            token: JWT token string
            
        Returns:
            dict: Token payload or None
        """
        try:
            return jwt.decode(
                token, 
                options={"verify_signature": False, "verify_exp": False}
            )
        except Exception as e:
            logger.error(f"Error decoding token payload: {e}")
            return None
