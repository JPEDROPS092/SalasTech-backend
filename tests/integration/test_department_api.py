"""
Integration tests for department management API endpoints.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from app.models.enums import UserRole

@pytest.mark.integration
class TestDepartmentAPI:
    """Integration tests for department management API endpoints."""
    
    def test_get_all_departments(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting all departments."""
        response = client.get("/api/departments", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify department data structure
        department = data[0]
        assert "id" in department
        assert "name" in department
        assert "code" in department
        assert "description" in department
    
    def test_get_department_by_id(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting a specific department by ID."""
        # Get a department ID from the seed data
        department_id = seed_test_data["departments"][0].id
        
        response = client.get(f"/api/departments/{department_id}", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        department = response.json()
        assert department["id"] == department_id
    
    def test_get_department_by_code(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting a department by code."""
        # Get a department code from the seed data
        department_code = seed_test_data["departments"][0].code
        
        response = client.get(f"/api/departments/code/{department_code}", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        department = response.json()
        assert department["code"] == department_code
    
    def test_create_department(self, client: TestClient, auth_headers, db_session):
        """Test creating a new department."""
        # Generate unique department code
        unique_code = f"TEST-{uuid.uuid4().hex[:6].upper()}"
        
        # Department data
        department_data = {
            "name": "Test Department API",
            "code": unique_code,
            "description": "Department created by API test",
            "budget": 100000.0,
            "manager_id": None
        }
        
        response = client.post("/api/departments", json=department_data, headers=auth_headers)
        
        # Check response
        assert response.status_code == 201
        created_department = response.json()
        assert created_department["name"] == department_data["name"]
        assert created_department["code"] == unique_code
        assert "id" in created_department
        
        # Verify department was created in the database
        from app.services.department_service import DepartmentService
        department_service = DepartmentService(db_session)
        department_in_db = department_service.get_department_by_id(created_department["id"])
        assert department_in_db is not None
        assert department_in_db.name == department_data["name"]
    
    def test_update_department(self, client: TestClient, auth_headers, seed_test_data):
        """Test updating a department."""
        # Get a department ID from the seed data
        department_id = seed_test_data["departments"][0].id
        
        # Update data
        update_data = {
            "name": "Updated Department Name",
            "description": "Updated by API test",
            "budget": 150000.0
        }
        
        response = client.put(f"/api/departments/{department_id}", json=update_data, headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        updated_department = response.json()
        assert updated_department["id"] == department_id
        assert updated_department["name"] == update_data["name"]
        assert updated_department["budget"] == update_data["budget"]
    
    def test_delete_department(self, client: TestClient, auth_headers, db_session):
        """Test deleting a department."""
        # Create a department to delete
        from app.services.department_service import DepartmentService
        
        department_service = DepartmentService(db_session)
        
        # Department data for creation
        department_data = {
            "name": "Department to Delete",
            "code": f"DEL-{uuid.uuid4().hex[:6].upper()}",
            "description": "Department to be deleted by API test",
            "budget": 50000.0
        }
        
        # Create department
        new_department = department_service.create_department(department_data)
        department_id = new_department.id
        
        # Delete the department
        response = client.delete(f"/api/departments/{department_id}", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        
        # Verify department was deleted
        deleted_department = department_service.get_department_by_id(department_id)
        assert deleted_department is None
    
    def test_assign_manager(self, client: TestClient, auth_headers, seed_test_data):
        """Test assigning a manager to a department."""
        # Get department and user IDs
        department_id = seed_test_data["departments"][0].id
        manager_id = seed_test_data["users"][0].id
        
        response = client.put(
            f"/api/departments/{department_id}/manager/{manager_id}", 
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        updated_department = response.json()
        assert updated_department["id"] == department_id
        assert updated_department["manager_id"] == manager_id
    
    def test_get_department_stats(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting department statistics."""
        # Get a department ID from the seed data
        department_id = seed_test_data["departments"][0].id
        
        response = client.get(f"/api/departments/{department_id}/stats", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        stats = response.json()
        assert "department_id" in stats
        assert "total_rooms" in stats
        assert "total_reservations" in stats
        assert "active_reservations" in stats
        assert stats["department_id"] == department_id
    
    def test_department_validation(self, client: TestClient, auth_headers):
        """Test department validation rules."""
        # Test 1: Missing required fields
        incomplete_data = {
            "name": "Incomplete Department",
            # Missing code
        }
        
        response = client.post("/api/departments", json=incomplete_data, headers=auth_headers)
        assert response.status_code in [400, 422]
        
        # Test 2: Duplicate code
        department_data_1 = {
            "name": "First Department",
            "code": "DUP-001",
            "description": "First department with duplicate code"
        }
        
        response = client.post("/api/departments", json=department_data_1, headers=auth_headers)
        assert response.status_code == 201
        
        # Try to create another with same code
        department_data_2 = {
            "name": "Second Department",
            "code": "DUP-001",  # Same code
            "description": "Second department with duplicate code"
        }
        
        response = client.post("/api/departments", json=department_data_2, headers=auth_headers)
        assert response.status_code in [400, 409]  # Should be rejected due to duplicate code
    
    def test_department_not_found(self, client: TestClient, auth_headers):
        """Test handling of non-existent departments."""
        # Test getting non-existent department
        response = client.get("/api/departments/99999", headers=auth_headers)
        assert response.status_code == 404
        
        # Test updating non-existent department
        update_data = {"name": "Updated Name"}
        response = client.put("/api/departments/99999", json=update_data, headers=auth_headers)
        assert response.status_code == 404
        
        # Test deleting non-existent department
        response = client.delete("/api/departments/99999", headers=auth_headers)
        assert response.status_code == 404
