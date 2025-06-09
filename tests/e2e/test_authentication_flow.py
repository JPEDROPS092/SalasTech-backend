"""
End-to-end tests for authentication flows.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from SalasTech.app.core.security import csrf

@pytest.mark.e2e
class TestAuthenticationFlow:
    """End-to-end tests for authentication flows."""
    
    def test_registration_login_logout_flow(self, client: TestClient, db_session):
        """Test the complete registration, login, and logout flow."""
        # Step 1: Visit the registration page
        response = client.get("/register")
        assert response.status_code == 200
        
        # Extract CSRF token from response cookies
        csrf_cookie = response.cookies.get(csrf.CSRF_COOKIE_NAME)
        assert csrf_cookie is not None
        
        # Step 2: Register a new user
        unique_email = f"e2e-test-{uuid.uuid4()}@example.com"
        register_data = {
            "name": "E2E",
            "surname": "Test User",
            "email": unique_email,
            "password": "SecurePassword123!",
            "confirmPassword": "SecurePassword123!",
            csrf.CSRF_FORM_FIELD: csrf_cookie
        }
        
        headers = {
            "Cookie": f"{csrf.CSRF_COOKIE_NAME}={csrf_cookie}"
        }
        
        response = client.post("/register", data=register_data, headers=headers)
        
        # Should redirect to success page or login
        assert response.status_code in [200, 302]
        
        # Step 3: Visit the login page
        response = client.get("/login")
        assert response.status_code == 200
        
        # Extract new CSRF token
        csrf_cookie = response.cookies.get(csrf.CSRF_COOKIE_NAME)
        assert csrf_cookie is not None
        
        # Step 4: Login with the newly created user
        login_data = {
            "username": unique_email,
            "password": "SecurePassword123!",
            csrf.CSRF_FORM_FIELD: csrf_cookie
        }
        
        headers = {
            "Cookie": f"{csrf.CSRF_COOKIE_NAME}={csrf_cookie}"
        }
        
        response = client.post("/api/auth/login", data=login_data, headers=headers)
        
        # Check login response
        assert response.status_code == 200
        assert "access_token" in response.json()
        
        # Extract session token from response
        token = response.json()["access_token"]
        
        # Step 5: Access a protected page (dashboard)
        auth_headers = {
            "Authorization": f"Bearer {token}",
            "Cookie": f"{csrf.CSRF_COOKIE_NAME}={csrf_cookie}"
        }
        
        response = client.get("/dashboard", headers=auth_headers)
        assert response.status_code == 200
        
        # Step 6: Logout
        response = client.get("/logout", headers=auth_headers)
        assert response.status_code in [200, 302]
        
        # Step 7: Verify cannot access protected page after logout
        response = client.get("/dashboard", headers=auth_headers)
        assert response.status_code in [302, 401, 403]  # Should redirect to login or return unauthorized
    
    def test_password_reset_flow(self, client: TestClient, db_session):
        """Test the password reset flow."""
        # Step 1: Visit the password reset page
        response = client.get("/password-reset")
        assert response.status_code == 200
        
        # Extract CSRF token
        csrf_cookie = response.cookies.get(csrf.CSRF_COOKIE_NAME)
        assert csrf_cookie is not None
        
        # Step 2: Request password reset for an existing user
        # First ensure the user exists
        from app.services.user_service import UserService
        user_service = UserService(db_session)
        email = "password-reset-test@example.com"
        password = "OldPassword123!"
        
        # Create user if not exists
        if not user_service.get_by_email(email):
            from app.models.dto import UserCreateDTO
            user_create = UserCreateDTO(
                name="Reset",
                surname="Test User",
                email=email,
                password=password
            )
            user_service.create_user(user_create)
        
        # Request password reset
        reset_data = {
            "email": email,
            csrf.CSRF_FORM_FIELD: csrf_cookie
        }
        
        headers = {
            "Cookie": f"{csrf.CSRF_COOKIE_NAME}={csrf_cookie}"
        }
        
        response = client.post("/password-reset", data=reset_data, headers=headers)
        assert response.status_code == 200
        
        # In a real test, we would extract the token from the response or database
        # For this test, we'll get it directly from the service
        token = user_service.generate_password_reset_token(email)
        
        # Step 3: Visit the password reset confirmation page with token
        response = client.get(f"/password-reset/{token}")
        assert response.status_code == 200
        
        # Extract new CSRF token
        csrf_cookie = response.cookies.get(csrf.CSRF_COOKIE_NAME)
        assert csrf_cookie is not None
        
        # Step 4: Submit new password
        new_password = "NewSecurePassword456!"
        reset_confirm_data = {
            "password": new_password,
            "confirmPassword": new_password,
            csrf.CSRF_FORM_FIELD: csrf_cookie
        }
        
        headers = {
            "Cookie": f"{csrf.CSRF_COOKIE_NAME}={csrf_cookie}"
        }
        
        response = client.post(f"/password-reset/{token}", data=reset_confirm_data, headers=headers)
        assert response.status_code in [200, 302]
        
        # Step 5: Try logging in with the new password
        response = client.get("/login")
        csrf_cookie = response.cookies.get(csrf.CSRF_COOKIE_NAME)
        
        login_data = {
            "username": email,
            "password": new_password,
            csrf.CSRF_FORM_FIELD: csrf_cookie
        }
        
        headers = {
            "Cookie": f"{csrf.CSRF_COOKIE_NAME}={csrf_cookie}"
        }
        
        response = client.post("/api/auth/login", data=login_data, headers=headers)
        assert response.status_code == 200
        assert "access_token" in response.json()
