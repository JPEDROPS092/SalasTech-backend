"""
Integration tests for room management API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.models.enums import RoomStatus

@pytest.mark.integration
class TestRoomAPI:
    """Integration tests for room management API endpoints."""
    
    def test_get_all_rooms(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting all rooms."""
        response = client.get("/api/rooms", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify room data structure
        room = data[0]
        assert "id" in room
        assert "name" in room
        assert "capacity" in room
        assert "status" in room
    
    def test_get_room_by_id(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting a specific room by ID."""
        # Get a room ID from the seed data
        room_id = seed_test_data["rooms"][0].id
        
        response = client.get(f"/api/rooms/{room_id}", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        room = response.json()
        assert room["id"] == room_id
    
    def test_create_room(self, client: TestClient, auth_headers, db_session):
        """Test creating a new room."""
        # Get a department ID
        from app.services.department_service import DepartmentService
        department_service = DepartmentService(db_session)
        departments = department_service.get_all_departments()
        department_id = departments[0].id
        
        # Room data
        room_data = {
            "code": "TEST-101",
            "name": "Test Room API",
            "capacity": 30,
            "building": "Test Building",
            "floor": "1st Floor",
            "department_id": department_id,
            "status": RoomStatus.ATIVA.value,
            "responsible": "API Test",
            "description": "Room created by API test"
        }
        
        response = client.post("/api/rooms", json=room_data, headers=auth_headers)
        
        # Check response
        assert response.status_code == 201
        created_room = response.json()
        assert created_room["name"] == room_data["name"]
        assert created_room["capacity"] == room_data["capacity"]
        
        # Verify room was created in the database
        from app.services.room_service import RoomService
        room_service = RoomService(db_session)
        room_in_db = room_service.get_room_by_id(created_room["id"])
        assert room_in_db is not None
        assert room_in_db.name == room_data["name"]
    
    def test_update_room(self, client: TestClient, auth_headers, seed_test_data):
        """Test updating a room."""
        # Get a room ID from the seed data
        room_id = seed_test_data["rooms"][0].id
        
        # Update data
        update_data = {
            "name": "Updated Room Name",
            "capacity": 50,
            "description": "Updated by API test"
        }
        
        response = client.put(f"/api/rooms/{room_id}", json=update_data, headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        updated_room = response.json()
        assert updated_room["id"] == room_id
        assert updated_room["name"] == update_data["name"]
        assert updated_room["capacity"] == update_data["capacity"]
    
    def test_delete_room(self, client: TestClient, auth_headers, db_session):
        """Test deleting a room."""
        # Create a room to delete
        from app.services.room_service import RoomService
        from app.services.department_service import DepartmentService
        
        room_service = RoomService(db_session)
        department_service = DepartmentService(db_session)
        departments = department_service.get_all_departments()
        
        # Room data for creation
        room_data = {
            "code": "DEL-101",
            "name": "Room to Delete",
            "capacity": 20,
            "building": "Test Building",
            "floor": "Ground Floor",
            "department_id": departments[0].id,
            "status": RoomStatus.ATIVA.value,
            "responsible": "API Test",
            "description": "Room to be deleted by API test"
        }
        
        # Create room
        new_room = room_service.create_room(room_data)
        room_id = new_room.id
        
        # Delete the room
        response = client.delete(f"/api/rooms/{room_id}", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        
        # Verify room was deleted
        deleted_room = room_service.get_room_by_id(room_id)
        assert deleted_room is None
    
    def test_get_available_rooms(self, client: TestClient, auth_headers):
        """Test getting available rooms for a time period."""
        from datetime import datetime, timedelta
        
        # Define time period for availability check
        now = datetime.now()
        start_time = (now + timedelta(days=1)).isoformat()
        end_time = (now + timedelta(days=1, hours=2)).isoformat()
        
        # Query parameters
        params = {
            "start_datetime": start_time,
            "end_datetime": end_time
        }
        
        response = client.get("/api/rooms/available", params=params, headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        available_rooms = response.json()
        assert isinstance(available_rooms, list)
        
        # All returned rooms should be active
        for room in available_rooms:
            assert room["status"] == RoomStatus.ATIVA.value
