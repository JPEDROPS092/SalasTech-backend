"""
Integration tests for authentication API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.models.enums import UserRole
from app.models.db import UsuarioDb
from app.core.security.password import PasswordManager
import uuid

@pytest.mark.integration
class TestAuthAPI:
    """Integration tests for authentication API endpoints."""
    
    def create_test_user(self, db_session, email="test@example.com", password="testpassword123"):
        """Helper method to create a test user."""
        # Create a test department if it doesn't exist
        from app.models.db import DepartamentoDb
        department = db_session.query(DepartamentoDb).first()
        if not department:
            department = DepartamentoDb(
                nome="Test Department",
                codigo="TEST",
                descricao="Test department for integration tests"
            )
            db_session.add(department)
            db_session.commit()
        
        # Create test user
        hashed_password = PasswordManager.hash_password(password)
        user = UsuarioDb(
            nome="Test",
            sobrenome="User",
            email=email,
            senha=hashed_password,
            papel=UserRole.USER,
            departamento_id=department.id
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_login_endpoint_success(self, client: TestClient, db_session):
        """Test successful login."""
        # Create test user
        email = "testuser@example.com"
        password = "testpassword123"
        self.create_test_user(db_session, email, password)
        
        # Login data
        login_data = {
            "email": email,
            "password": password
        }
        
        # Make login request
        response = client.post("/auth/login", json=login_data)
        
        # Verify response
        assert response.status_code == 200
        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"
        assert "expires_in" in response_data
    
    def test_login_endpoint_invalid_email(self, client: TestClient, db_session):
        """Test login with invalid email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"
    
    def test_login_endpoint_invalid_password(self, client: TestClient, db_session):
        """Test login with invalid password."""
        # Create test user
        email = "testuser2@example.com" 
        password = "testpassword123"
        self.create_test_user(db_session, email, password)
        
        # Try login with wrong password
        login_data = {
            "email": email,
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"
    
    def test_refresh_token_endpoint(self, client: TestClient, db_session):
        """Test token refresh endpoint."""
        # Create test user and login first
        email = "testuser3@example.com"
        password = "testpassword123"
        self.create_test_user(db_session, email, password)
        
        # Login to get tokens
        login_data = {
            "email": email,
            "password": password
        }
        
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        tokens = login_response.json()
        refresh_token = tokens["refresh_token"]
        
        # Test token refresh
        refresh_data = {
            "refresh_token": refresh_token
        }
        
        response = client.post("/auth/refresh", json=refresh_data)
        
        # Verify response
        assert response.status_code == 200
        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token."""
        refresh_data = {
            "refresh_token": "invalid_token"
        }
        
        response = client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired refresh token"
    
    def test_get_profile_endpoint(self, client: TestClient, db_session):
        """Test get user profile endpoint."""
        # Create test user and login
        email = "testuser4@example.com"
        password = "testpassword123"
        user = self.create_test_user(db_session, email, password)
        
        # Login to get token
        login_data = {
            "email": email,
            "password": password
        }
        
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        tokens = login_response.json()
        access_token = tokens["access_token"]
        
        # Get profile
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = client.get("/auth/me", headers=headers)
        
        # Verify response
        assert response.status_code == 200
        profile_data = response.json()
        assert profile_data["email"] == email
        assert profile_data["name"] == user.nome
        assert "id" in profile_data
        assert "role" in profile_data
    
    def test_verify_token_endpoint(self, client: TestClient, db_session):
        """Test token verification endpoint."""
        # Create test user and login
        email = "testuser5@example.com"
        password = "testpassword123"
        self.create_test_user(db_session, email, password)
        
        # Login to get token
        login_data = {
            "email": email,
            "password": password
        }
        
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        tokens = login_response.json()
        access_token = tokens["access_token"]
        
        # Verify token
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = client.get("/auth/verify", headers=headers)
        
        # Verify response
        assert response.status_code == 200
        verify_data = response.json()
        assert verify_data["valid"] is True
        assert "user_id" in verify_data
        assert "role" in verify_data
    
    def test_logout_endpoint(self, client: TestClient, db_session):
        """Test logout endpoint."""
        # Create test user and login
        email = "testuser6@example.com"
        password = "testpassword123"
        self.create_test_user(db_session, email, password)
        
        # Login to get token
        login_data = {
            "email": email,
            "password": password
        }
        
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        tokens = login_response.json()
        access_token = tokens["access_token"]
        
        # Logout
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = client.post("/auth/logout", headers=headers)
        
        # Verify response
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"
    
    def test_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token."""
        response = client.get("/auth/me")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token."""
        headers = {
            "Authorization": "Bearer invalid_token"
        }
        
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401
