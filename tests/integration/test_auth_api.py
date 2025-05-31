"""
Integration tests for authentication API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.core.security import csrf

@pytest.mark.integration
class TestAuthAPI:
    """Integration tests for authentication API endpoints."""
    
    def test_login_endpoint(self, client: TestClient, db_session):
        """Test the login endpoint."""
        # First get the login page to get a CSRF token
        response = client.get("/login")
        assert response.status_code == 200
        
        # Extract CSRF token from response cookies
        csrf_cookie = response.cookies.get(csrf.CSRF_COOKIE_NAME)
        assert csrf_cookie is not None
        
        # Attempt login with valid credentials
        login_data = {
            "username": "admin@example.com",  # This should match a user in your test database
            "password": "admin123",
            csrf.CSRF_FORM_FIELD: csrf_cookie
        }
        
        headers = {
            "Cookie": f"{csrf.CSRF_COOKIE_NAME}={csrf_cookie}"
        }
        
        response = client.post("/api/auth/login", data=login_data, headers=headers)
        
        # Check response
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    def test_login_rate_limiting(self, client: TestClient, db_session, monkeypatch):
        """Test rate limiting on login endpoint."""
        # Re-enable rate limiting for this test
        from app.core.security.rate_limiter import RateLimiter
        
        # Mock the rate limiter to allow only 2 attempts
        original_check = RateLimiter.check_login_rate_limit
        
        attempt_count = 0
        def mock_check_rate_limit(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count > 2:
                from fastapi import HTTPException
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        monkeypatch.setattr(RateLimiter, "check_login_rate_limit", mock_check_rate_limit)
        
        # Get CSRF token
        response = client.get("/login")
        csrf_cookie = response.cookies.get(csrf.CSRF_COOKIE_NAME)
        
        # Attempt login with invalid credentials multiple times
        login_data = {
            "username": "test@example.com",
            "password": "wrongpassword",
            csrf.CSRF_FORM_FIELD: csrf_cookie
        }
        
        headers = {
            "Cookie": f"{csrf.CSRF_COOKIE_NAME}={csrf_cookie}"
        }
        
        # First two attempts should return 401 (unauthorized)
        for _ in range(2):
            response = client.post("/api/auth/login", data=login_data, headers=headers)
            assert response.status_code == 401
        
        # Third attempt should be rate limited
        response = client.post("/api/auth/login", data=login_data, headers=headers)
        assert response.status_code == 429
        
        # Restore original rate limiter
        monkeypatch.setattr(RateLimiter, "check_login_rate_limit", original_check)
    
    def test_csrf_protection(self, client: TestClient, db_session):
        """Test CSRF protection on login endpoint."""
        # Attempt login without CSRF token
        login_data = {
            "username": "admin@example.com",
            "password": "admin123"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        # Should be rejected due to missing CSRF token
        assert response.status_code == 403
        
        # Now try with invalid CSRF token
        login_data[csrf.CSRF_FORM_FIELD] = "invalid_token"
        headers = {
            "Cookie": f"{csrf.CSRF_COOKIE_NAME}=invalid_token"
        }
        
        response = client.post("/api/auth/login", data=login_data, headers=headers)
        
        # Should be rejected due to invalid CSRF token
        assert response.status_code == 403
    
    def test_register_endpoint(self, client: TestClient, db_session):
        """Test the registration endpoint."""
        # First get the register page to get a CSRF token
        response = client.get("/register")
        assert response.status_code == 200
        
        # Extract CSRF token from response cookies
        csrf_cookie = response.cookies.get(csrf.CSRF_COOKIE_NAME)
        assert csrf_cookie is not None
        
        # Generate a unique email for this test
        import uuid
        unique_email = f"test-{uuid.uuid4()}@example.com"
        
        # Attempt registration with valid data
        register_data = {
            "name": "Test",
            "surname": "User",
            "email": unique_email,
            "password": "securepassword123",
            "confirmPassword": "securepassword123",
            csrf.CSRF_FORM_FIELD: csrf_cookie
        }
        
        headers = {
            "Cookie": f"{csrf.CSRF_COOKIE_NAME}={csrf_cookie}"
        }
        
        response = client.post("/register", data=register_data, headers=headers)
        
        # Check response - should be a redirect to login or success page
        assert response.status_code in [200, 302]
        
        # Verify the user was created in the database
        from app.services.user_service import UserService
        user_service = UserService(db_session)
        created_user = user_service.get_by_email(unique_email)
        assert created_user is not None
        assert created_user.email == unique_email
    
    def test_logout_endpoint(self, client: TestClient, auth_headers):
        """Test the logout endpoint."""
        # First login to get a session
        response = client.get("/logout", headers=auth_headers)
        
        # Should redirect to home or login page
        assert response.status_code in [200, 302]
        
        # Check that session cookie is cleared
        assert "Set-Cookie" in response.headers
        cookie_header = response.headers["Set-Cookie"]
        assert "Max-Age=0" in cookie_header or "Expires" in cookie_header
