"""
Integration tests for user management API endpoints.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from app.models.enums import UserRole

@pytest.mark.integration
class TestUserAPI:
    """Integration tests for user management API endpoints."""
    
    def test_get_all_users(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting all users."""
        response = client.get("/api/users", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify user data structure
        user = data[0]
        assert "id" in user
        assert "name" in user
        assert "surname" in user
        assert "email" in user
        assert "role" in user
        assert "password" not in user  # Password should not be returned
    
    def test_get_user_by_id(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting a specific user by ID."""
        # Get a user ID from the seed data
        user_id = seed_test_data["users"][0].id
        
        response = client.get(f"/api/users/{user_id}", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        user = response.json()
        assert user["id"] == user_id
        assert "password" not in user  # Password should not be returned
    
    def test_get_current_user(self, client: TestClient, auth_headers):
        """Test getting the current authenticated user."""
        response = client.get("/api/users/me", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        user = response.json()
        assert "id" in user
        assert "name" in user
        assert "email" in user
        assert "password" not in user  # Password should not be returned
    
    def test_create_user(self, client: TestClient, auth_headers, db_session):
        """Test creating a new user."""
        # Generate unique email for the test
        unique_email = f"test-user-{uuid.uuid4()}@example.com"
        
        # User data
        user_data = {
            "name": "Test",
            "surname": "User",
            "email": unique_email,
            "password": "SecurePassword123!",
            "role": UserRole.USUARIO.value
        }
        
        response = client.post("/api/users", json=user_data, headers=auth_headers)
        
        # Check response
        assert response.status_code == 201
        created_user = response.json()
        assert created_user["name"] == user_data["name"]
        assert created_user["email"] == unique_email
        assert created_user["role"] == UserRole.USUARIO.value
        assert "password" not in created_user  # Password should not be returned
        
        # Verify user was created in the database
        from app.services.user_service import UserService
        user_service = UserService(db_session)
        user_in_db = user_service.get_by_email(unique_email)
        assert user_in_db is not None
        assert user_in_db.name == user_data["name"]
    
    def test_update_user(self, client: TestClient, auth_headers, seed_test_data):
        """Test updating a user."""
        # Get a user ID from the seed data
        user_id = seed_test_data["users"][0].id
        
        # Update data
        update_data = {
            "name": "Updated",
            "surname": "User Name"
        }
        
        response = client.put(f"/api/users/{user_id}", json=update_data, headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["id"] == user_id
        assert updated_user["name"] == update_data["name"]
        assert updated_user["surname"] == update_data["surname"]
    
    def test_delete_user(self, client: TestClient, auth_headers, db_session):
        """Test deleting a user."""
        # Create a user to delete
        from app.services.user_service import UserService
        
        user_service = UserService(db_session)
        unique_email = f"delete-test-{uuid.uuid4()}@example.com"
        
        # User data for creation
        user_data = {
            "name": "Delete",
            "surname": "Test User",
            "email": unique_email,
            "password": "DeletePassword123!",
            "role": UserRole.USUARIO.value
        }
        
        # Create user
        new_user = user_service.create_user(user_data)
        user_id = new_user.id
        
        # Delete the user
        response = client.delete(f"/api/users/{user_id}", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        
        # Verify user was deleted
        deleted_user = user_service.get_by_id(user_id)
        assert deleted_user is None
    
    def test_change_password(self, client: TestClient, auth_headers, db_session):
        """Test changing a user's password."""
        # Create a user for password change
        from app.services.user_service import UserService
        
        user_service = UserService(db_session)
        unique_email = f"pwd-change-{uuid.uuid4()}@example.com"
        old_password = "OldPassword123!"
        
        # User data for creation
        user_data = {
            "name": "Password",
            "surname": "Change Test",
            "email": unique_email,
            "password": old_password,
            "role": UserRole.USUARIO.value
        }
        
        # Create user
        new_user = user_service.create_user(user_data)
        user_id = new_user.id
        
        # Change password data
        new_password = "NewPassword456!"
        password_data = {
            "current_password": old_password,
            "new_password": new_password
        }
        
        # Login with this user to get their token
        from app.core.security.session import create_access_token
        from app.models.dto import UserLoginDTO
        
        user_login = UserLoginDTO(email=unique_email, password=old_password)
        token = create_access_token(user_login)
        
        user_auth_headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Change password
        response = client.post(f"/api/users/{user_id}/change-password", 
                              json=password_data, 
                              headers=user_auth_headers)
        
        # Check response
        assert response.status_code == 200
        
        # Verify password was changed by trying to login with new password
        from app.services.auth_service import AuthService
        
        auth_service = AuthService(db_session)
        login_result = auth_service.authenticate_user(unique_email, new_password)
        assert login_result is not None
        
        # Old password should no longer work
        login_result = auth_service.authenticate_user(unique_email, old_password)
        assert login_result is None
    
    def test_update_user_role(self, client: TestClient, auth_headers, db_session):
        """Test updating a user's role (admin operation)."""
        # Create a user for role update
        from app.services.user_service import UserService
        
        user_service = UserService(db_session)
        unique_email = f"role-update-{uuid.uuid4()}@example.com"
        
        # User data for creation with initial role
        user_data = {
            "name": "Role",
            "surname": "Update Test",
            "email": unique_email,
            "password": "RolePassword123!",
            "role": UserRole.USUARIO.value
        }
        
        # Create user
        new_user = user_service.create_user(user_data)
        user_id = new_user.id
        
        # Update role data
        role_data = {
            "role": UserRole.ADMINISTRADOR.value
        }
        
        # Update role (using admin auth headers)
        response = client.put(f"/api/users/{user_id}/role", 
                             json=role_data, 
                             headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["id"] == user_id
        assert updated_user["role"] == UserRole.ADMINISTRADOR.value
        
        # Verify role was updated in the database
        user_in_db = user_service.get_by_id(user_id)
        assert user_in_db.role == UserRole.ADMINISTRADOR
