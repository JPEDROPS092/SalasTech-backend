"""
Unit tests for security features.
"""

import pytest
import time
from unittest.mock import MagicMock, patch
from fastapi import Request, HTTPException
from fastapi.responses import Response

from app.core.security.rate_limiter import RateLimiter
from app.core.security.csrf import CSRFProtection, CSRF_COOKIE_NAME, CSRF_HEADER_NAME, CSRF_FORM_FIELD
from app.core.security.session import create_access_token, verify_token, get_current_user


class TestRateLimiter:
    """Tests for the rate limiter implementation."""
    
    def test_init(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(max_requests=5, window_seconds=60, block_time_seconds=300)
        assert limiter.max_requests == 5
        assert limiter.window_seconds == 60
        assert limiter.block_time_seconds == 300
        assert limiter.request_records == {}
        assert limiter.blocked_keys == {}
    
    def test_is_rate_limited_under_limit(self):
        """Test rate limiting when under the limit."""
        limiter = RateLimiter(max_requests=5, window_seconds=60, block_time_seconds=300)
        
        # Make a few requests (under the limit)
        for i in range(3):
            is_limited, retry_after = limiter.is_rate_limited("test_key")
            assert is_limited is False
            assert retry_after is None
    
    def test_is_rate_limited_over_limit(self):
        """Test rate limiting when over the limit."""
        limiter = RateLimiter(max_requests=3, window_seconds=60, block_time_seconds=300)
        
        # Make requests up to the limit
        for i in range(3):
            is_limited, retry_after = limiter.is_rate_limited("test_key")
            assert is_limited is False
            assert retry_after is None
        
        # Make one more request (over the limit)
        is_limited, retry_after = limiter.is_rate_limited("test_key")
        assert is_limited is True
        assert retry_after is not None
        assert retry_after <= 300  # Should be blocked for up to block_time_seconds
    
    def test_is_rate_limited_different_keys(self):
        """Test rate limiting with different keys."""
        limiter = RateLimiter(max_requests=3, window_seconds=60, block_time_seconds=300)
        
        # Make requests for key1 up to the limit
        for i in range(3):
            is_limited, retry_after = limiter.is_rate_limited("key1")
            assert is_limited is False
            assert retry_after is None
        
        # Key1 should now be rate limited
        is_limited, retry_after = limiter.is_rate_limited("key1")
        assert is_limited is True
        assert retry_after is not None
        
        # Key2 should not be rate limited
        is_limited, retry_after = limiter.is_rate_limited("key2")
        assert is_limited is False
        assert retry_after is None
    
    def test_cleanup_expired_records(self):
        """Test cleanup of expired records."""
        limiter = RateLimiter(max_requests=5, window_seconds=1, block_time_seconds=2)
        
        # Make a few requests
        for i in range(3):
            limiter.is_rate_limited("test_key")
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Records should be cleaned up on next check
        is_limited, retry_after = limiter.is_rate_limited("test_key")
        assert is_limited is False
        assert retry_after is None
        assert len(limiter.request_records["test_key"]) == 1  # Only the new request
    
    def test_check_login_rate_limit(self):
        """Test the login rate limit check."""
        # Mock request with client IP
        mock_request = MagicMock()
        mock_request.client.host = "192.168.1.1"
        
        # Patch the is_rate_limited method to return not limited
        with patch.object(RateLimiter, 'is_rate_limited', return_value=(False, None)):
            # Should not raise an exception
            RateLimiter.check_login_rate_limit(mock_request)
        
        # Patch to return limited
        with patch.object(RateLimiter, 'is_rate_limited', return_value=(True, 300)):
            # Should raise an HTTPException
            with pytest.raises(HTTPException) as excinfo:
                RateLimiter.check_login_rate_limit(mock_request)
            assert excinfo.value.status_code == 429
            assert "Too many login attempts" in excinfo.value.detail


class TestCSRFProtection:
    """Tests for CSRF protection implementation."""
    
    def test_generate_token(self):
        """Test CSRF token generation."""
        # Generate a token
        token = CSRFProtection.generate_token()
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20  # Token should be reasonably long
        
        # Generate a token with user ID
        token_with_user = CSRFProtection.generate_token("user123")
        assert token_with_user is not None
        assert isinstance(token_with_user, str)
        assert token != token_with_user  # Tokens should be different
    
    def test_validate_token(self):
        """Test CSRF token validation."""
        # Generate a valid token
        token = CSRFProtection.generate_token()
        
        # Validate the token
        assert CSRFProtection.validate_token(token) is True
        
        # Validate an invalid token
        assert CSRFProtection.validate_token("invalid_token") is False
        assert CSRFProtection.validate_token("") is False
        assert CSRFProtection.validate_token(None) is False
    
    def test_set_csrf_cookie(self):
        """Test setting CSRF cookie."""
        # Mock response
        mock_response = MagicMock()
        mock_response.set_cookie = MagicMock()
        
        # Set CSRF cookie
        token = "test_csrf_token"
        CSRFProtection.set_csrf_cookie(mock_response, token)
        
        # Verify set_cookie was called with correct parameters
        mock_response.set_cookie.assert_called_once()
        args, kwargs = mock_response.set_cookie.call_args
        assert kwargs["key"] == CSRF_COOKIE_NAME
        assert kwargs["value"] == token
        assert kwargs["httponly"] is True
        assert kwargs["secure"] is True
        assert kwargs["samesite"] in ["lax", "Lax"]
    
    def test_get_csrf_token_from_request(self):
        """Test getting CSRF token from request."""
        # Mock request with CSRF token in header
        mock_request = MagicMock()
        mock_request.headers = {CSRF_HEADER_NAME: "header_token"}
        mock_request.cookies = {CSRF_COOKIE_NAME: "cookie_token"}
        
        # Should prefer header token
        token = CSRFProtection.get_csrf_token_from_request(mock_request)
        assert token == "header_token"
        
        # Mock request with only cookie token
        mock_request.headers = {}
        token = CSRFProtection.get_csrf_token_from_request(mock_request)
        assert token == "cookie_token"
        
        # Mock request with no token
        mock_request.cookies = {}
        token = CSRFProtection.get_csrf_token_from_request(mock_request)
        assert token is None


class TestSessionSecurity:
    """Tests for session security implementation."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        from app.models.dto import UserLoginDTO
        
        # Create a user login DTO
        user_login = UserLoginDTO(email="test@example.com", password="password123")
        
        # Create an access token
        token = create_access_token(user_login)
        assert token is not None
        assert isinstance(token, str)
    
    def test_verify_token_valid(self):
        """Test verification of a valid token."""
        from app.models.dto import UserLoginDTO
        
        # Create a user login DTO
        user_login = UserLoginDTO(email="test@example.com", password="password123")
        
        # Create an access token
        token = create_access_token(user_login)
        
        # Verify the token
        payload = verify_token(token)
        assert payload is not None
        assert "sub" in payload
        assert payload["sub"] == "test@example.com"
    
    def test_verify_token_invalid(self):
        """Test verification of an invalid token."""
        # Try to verify an invalid token
        with pytest.raises(HTTPException) as excinfo:
            verify_token("invalid_token")
        assert excinfo.value.status_code == 401
        assert "Invalid token" in excinfo.value.detail
    
    def test_get_current_user(self):
        """Test getting the current user from a token."""
        # This test requires mocking the database and user service
        # For simplicity, we'll just test the error case
        mock_request = MagicMock()
        mock_request.cookies = {}
        
        # Should raise an exception when no token is provided
        with pytest.raises(HTTPException) as excinfo:
            get_current_user(mock_request)
        assert excinfo.value.status_code == 401
