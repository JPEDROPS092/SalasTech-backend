"""
Rate limiter implementation for FastAPI
Provides protection against brute force attacks by limiting the number of requests
from a single IP address or user in a given time period.
"""

import time
from typing import Dict, Tuple, Optional, Callable, Any
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

# Configure logger
logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiter implementation that tracks requests by IP address or custom key.
    """
    def __init__(self, window_seconds: int = 60, max_requests: int = 5, block_time: int = 300):
        """
        Initialize the rate limiter.
        
        Args:
            window_seconds: Time window in seconds to track requests
            max_requests: Maximum number of requests allowed in the window
            block_time: Time in seconds to block after exceeding max_requests
        """
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self.block_time = block_time
        # Store request timestamps by IP or key
        self.request_log: Dict[str, list] = {}
        # Store blocked status and unblock time
        self.blocked: Dict[str, int] = {}
    
    def is_rate_limited(self, key: str) -> Tuple[bool, Optional[int]]:
        """
        Check if a key is rate limited.
        
        Args:
            key: The key to check (IP address or user identifier)
            
        Returns:
            Tuple of (is_limited, retry_after)
        """
        current_time = time.time()
        
        # Check if the key is blocked
        if key in self.blocked:
            unblock_time = self.blocked[key]
            if current_time < unblock_time:
                # Still blocked
                return True, int(unblock_time - current_time)
            else:
                # Unblock if block time has passed
                del self.blocked[key]
                if key in self.request_log:
                    del self.request_log[key]
        
        # Initialize request log for this key if it doesn't exist
        if key not in self.request_log:
            self.request_log[key] = []
        
        # Clean up old requests outside the window
        window_start = current_time - self.window_seconds
        self.request_log[key] = [t for t in self.request_log[key] if t >= window_start]
        
        # Check if the number of requests exceeds the limit
        if len(self.request_log[key]) >= self.max_requests:
            # Block the key
            block_until = current_time + self.block_time
            self.blocked[key] = block_until
            logger.warning(f"Rate limit exceeded for {key}. Blocked until {time.ctime(block_until)}")
            return True, self.block_time
        
        # Add the current request
        self.request_log[key].append(current_time)
        return False, None
    
    def get_remaining(self, key: str) -> int:
        """
        Get the number of remaining requests allowed for a key.
        
        Args:
            key: The key to check
            
        Returns:
            Number of remaining requests
        """
        if key in self.blocked:
            return 0
        
        if key not in self.request_log:
            return self.max_requests
        
        # Clean up old requests
        current_time = time.time()
        window_start = current_time - self.window_seconds
        self.request_log[key] = [t for t in self.request_log[key] if t >= window_start]
        
        return max(0, self.max_requests - len(self.request_log[key]))

# Global rate limiter instances
# For login attempts (5 attempts per minute, block for 5 minutes)
login_limiter = RateLimiter(window_seconds=60, max_requests=5, block_time=300)

# For password reset attempts (3 attempts per 10 minutes, block for 30 minutes)
password_reset_limiter = RateLimiter(window_seconds=600, max_requests=3, block_time=1800)

# For API requests (60 requests per minute)
api_limiter = RateLimiter(window_seconds=60, max_requests=60, block_time=300)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply rate limiting to all requests or specific paths.
    """
    def __init__(
        self, 
        app: ASGIApp, 
        limiter: RateLimiter = api_limiter,
        key_func: Callable[[Request], str] = None,
        exclude_paths: list = None
    ):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
            limiter: The rate limiter to use
            key_func: Function to extract the key from the request (defaults to client IP)
            exclude_paths: List of paths to exclude from rate limiting
        """
        super().__init__(app)
        self.limiter = limiter
        self.key_func = key_func or self._default_key_func
        self.exclude_paths = exclude_paths or []
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request and apply rate limiting if needed.
        """
        # Skip rate limiting for excluded paths
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return await call_next(request)
        
        # Get the key for this request
        key = self.key_func(request)
        
        # Check if rate limited
        is_limited, retry_after = self.limiter.is_rate_limited(key)
        
        if is_limited:
            # Return 429 Too Many Requests
            headers = {"Retry-After": str(retry_after)}
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers=headers
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to the response
        remaining = self.limiter.get_remaining(key)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.max_requests)
        
        return response
    
    @staticmethod
    def _default_key_func(request: Request) -> str:
        """
        Default function to extract key from request (uses client IP).
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Get the first IP in the chain
            return forwarded.split(",")[0].strip()
        
        # Fallback to client host
        return request.client.host if request.client else "unknown"

def check_login_rate_limit(request: Request):
    """
    Check if login attempts are rate limited for the current IP.
    Raises HTTPException if rate limited.
    """
    client_ip = RateLimitMiddleware._default_key_func(request)
    is_limited, retry_after = login_limiter.is_rate_limited(client_ip)
    
    if is_limited:
        headers = {"Retry-After": str(retry_after)}
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Try again in {retry_after} seconds.",
            headers=headers
        )

def check_password_reset_rate_limit(request: Request):
    """
    Check if password reset attempts are rate limited for the current IP.
    Raises HTTPException if rate limited.
    """
    client_ip = RateLimitMiddleware._default_key_func(request)
    is_limited, retry_after = password_reset_limiter.is_rate_limited(client_ip)
    
    if is_limited:
        headers = {"Retry-After": str(retry_after)}
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many password reset attempts. Try again in {retry_after} seconds.",
            headers=headers
        )

def apply_rate_limiting(app: ASGIApp):
    """
    Apply rate limiting middleware to the application.
    """
    app.add_middleware(
        RateLimitMiddleware,
        limiter=api_limiter,
        exclude_paths=["/static/", "/favicon.ico"]
    )
    
    logger.info("Rate limiting middleware applied to the application")
