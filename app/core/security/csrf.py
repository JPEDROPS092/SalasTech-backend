"""
CSRF (Cross-Site Request Forgery) protection for FastAPI.
Implements token generation, validation, and middleware to protect forms.
"""

import secrets
import time
import hashlib
import hmac
import base64
from typing import Optional, List, Dict, Any
from fastapi import Request, Response, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
from app.core.config import CONFIG

# Configure logger
logger = logging.getLogger(__name__)

# CSRF token configuration
CSRF_SECRET = CONFIG.HASH_SALT.encode()  # Use the same secret as JWT for simplicity
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_FORM_FIELD = "csrf_token"
CSRF_TOKEN_LIFETIME = 3600  # 1 hour in seconds

class CSRFProtection:
    """
    CSRF protection implementation.
    """
    @staticmethod
    def generate_token(user_id: Optional[str] = None) -> str:
        """
        Generate a new CSRF token.
        
        Args:
            user_id: Optional user identifier to bind the token to
            
        Returns:
            Base64 encoded CSRF token
        """
        # Generate a random token
        random_bytes = secrets.token_bytes(32)
        
        # Current timestamp
        timestamp = int(time.time())
        
        # Create payload
        payload = f"{timestamp}"
        if user_id:
            payload += f"|{user_id}"
        
        # Encode payload
        payload_bytes = payload.encode()
        
        # Create signature using HMAC-SHA256
        signature = hmac.new(
            CSRF_SECRET,
            random_bytes + payload_bytes,
            hashlib.sha256
        ).digest()
        
        # Combine random bytes, payload, and signature
        token_bytes = random_bytes + payload_bytes + signature
        
        # Encode as base64
        token = base64.urlsafe_b64encode(token_bytes).decode()
        
        return token
    
    @staticmethod
    def validate_token(token: str, user_id: Optional[str] = None) -> bool:
        """
        Validate a CSRF token.
        
        Args:
            token: The token to validate
            user_id: Optional user identifier to check against the token
            
        Returns:
            True if the token is valid, False otherwise
        """
        try:
            # Decode from base64
            token_bytes = base64.urlsafe_b64decode(token)
            
            # Extract components
            random_bytes = token_bytes[:32]
            
            # Find the signature (last 32 bytes)
            signature = token_bytes[-32:]
            
            # Everything between random bytes and signature is the payload
            payload_bytes = token_bytes[32:-32]
            payload = payload_bytes.decode()
            
            # Verify signature
            expected_signature = hmac.new(
                CSRF_SECRET,
                random_bytes + payload_bytes,
                hashlib.sha256
            ).digest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("CSRF token signature mismatch")
                return False
            
            # Parse payload
            parts = payload.split("|")
            timestamp = int(parts[0])
            
            # Check if token has expired
            if time.time() - timestamp > CSRF_TOKEN_LIFETIME:
                logger.warning("CSRF token expired")
                return False
            
            # Check user_id if provided
            if user_id and len(parts) > 1:
                token_user_id = parts[1]
                if token_user_id != user_id:
                    logger.warning(f"CSRF token user mismatch: {token_user_id} != {user_id}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating CSRF token: {e}")
            return False
    
    @staticmethod
    def set_csrf_cookie(response: Response, token: str):
        """
        Set the CSRF token cookie.
        
        Args:
            response: The response to set the cookie on
            token: The CSRF token
        """
        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=token,
            httponly=True,
            secure=True,  # True in production
            samesite="lax",  # Prevents CSRF while allowing normal navigation
            max_age=CSRF_TOKEN_LIFETIME
        )
    
    @staticmethod
    async def get_csrf_token_from_request(request: Request) -> Optional[str]:
        """
        Get the CSRF token from a request.
        Checks headers, cookies, and form data.
        
        Args:
            request: The request to get the token from
            
        Returns:
            The CSRF token if found, None otherwise
        """
        # Check header first
        token = request.headers.get(CSRF_HEADER_NAME)
        if token:
            return token
        
        # Check cookies
        token = request.cookies.get(CSRF_COOKIE_NAME)
        if token:
            return token
        
        # Check form data
        try:
            # Use a safe approach to get form data
            if hasattr(request, "_form") and request._form is not None:
                form_data = await request.form()
                token = form_data.get(CSRF_FORM_FIELD)
                if token:
                    return token
            else:
                # Only try to get form data if it's likely to exist (based on content type)
                content_type = request.headers.get("content-type", "")
                if "form" in content_type.lower():
                    form_data = await request.form()
                    token = form_data.get(CSRF_FORM_FIELD)
                    if token:
                        return token
        except Exception as e:
            logger.error(f"Error getting form data: {e}")
            pass
        
        return None

class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware for CSRF protection.
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        exclude_paths: List[str] = None,
        exclude_methods: List[str] = None
    ):
        """
        Initialize the CSRF middleware.
        
        Args:
            app: The ASGI application
            exclude_paths: List of paths to exclude from CSRF protection
            exclude_methods: List of HTTP methods to exclude from CSRF protection
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/static/", "/api/", "/docs", "/redoc", "/openapi.json"]
        self.exclude_methods = exclude_methods or ["GET", "HEAD", "OPTIONS"]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request and enforce CSRF protection if needed.
        """
        # Skip CSRF check for excluded paths
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return await call_next(request)
        
        # Skip CSRF check for excluded methods
        if request.method in self.exclude_methods:
            response = await call_next(request)
            
            # For GET requests, set a new CSRF token if not present
            if request.method == "GET" and CSRF_COOKIE_NAME not in request.cookies:
                token = CSRFProtection.generate_token()
                CSRFProtection.set_csrf_cookie(response, token)
            
            return response
        
        # For other methods (POST, PUT, DELETE, etc.), validate CSRF token
        token = await CSRFProtection.get_csrf_token_from_request(request)
        
        if not token or not CSRFProtection.validate_token(token):
            logger.warning(f"CSRF validation failed for {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing or invalid"
            )
        
        # Token is valid, process the request
        response = await call_next(request)
        
        # Generate a new token for the next request
        new_token = CSRFProtection.generate_token()
        CSRFProtection.set_csrf_cookie(response, new_token)
        
        return response

# Dependency for CSRF protection in route handlers
async def csrf_protect(request: Request):
    """
    Dependency for CSRF protection in route handlers.
    Raises HTTPException if CSRF token is missing or invalid.
    """
    token = await CSRFProtection.get_csrf_token_from_request(request)
    
    if not token or not CSRFProtection.validate_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing or invalid"
        )
    
    return token

def apply_csrf_middleware(app: ASGIApp) -> None:
    """
    Apply CSRF protection middleware to the application.
    
    Args:
        app: The ASGI application
    """
    app.add_middleware(
        CSRFMiddleware,
        exclude_paths=["/static/", "/api/", "/docs", "/redoc", "/openapi.json", "/favicon.ico"]
    )
    
    logger.info("CSRF protection middleware applied to the application")
