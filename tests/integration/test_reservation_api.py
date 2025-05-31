"""
Integration tests for reservation management API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.models.enums import ReservationStatus

@pytest.mark.integration
class TestReservationAPI:
    """Integration tests for reservation management API endpoints."""
    
    def test_get_all_reservations(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting all reservations."""
        response = client.get("/api/reservations", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify reservation data structure
        reservation = data[0]
        assert "id" in reservation
        assert "room_id" in reservation
        assert "user_id" in reservation
        assert "title" in reservation
        assert "start_datetime" in reservation
        assert "end_datetime" in reservation
        assert "status" in reservation
    
    def test_get_reservation_by_id(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting a specific reservation by ID."""
        # Get a reservation ID from the seed data
        reservation_id = seed_test_data["reservations"][0].id
        
        response = client.get(f"/api/reservations/{reservation_id}", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        reservation = response.json()
        assert reservation["id"] == reservation_id
    
    def test_create_reservation(self, client: TestClient, auth_headers, db_session, seed_test_data):
        """Test creating a new reservation."""
        # Get room and user IDs
        room_id = seed_test_data["rooms"][0].id
        user_id = seed_test_data["users"][0].id
        
        # Define time period for the reservation
        now = datetime.now()
        start_datetime = (now + timedelta(days=3)).isoformat()
        end_datetime = (now + timedelta(days=3, hours=2)).isoformat()
        
        # Reservation data
        reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": "Test Reservation API",
            "description": "Reservation created by API test",
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "status": ReservationStatus.PENDENTE.value
        }
        
        response = client.post("/api/reservations", json=reservation_data, headers=auth_headers)
        
        # Check response
        assert response.status_code == 201
        created_reservation = response.json()
        assert created_reservation["title"] == reservation_data["title"]
        assert created_reservation["room_id"] == room_id
        assert created_reservation["user_id"] == user_id
        
        # Verify reservation was created in the database
        from app.services.reservation_service import ReservationService
        reservation_service = ReservationService(db_session)
        reservation_in_db = reservation_service.get_reservation_by_id(created_reservation["id"])
        assert reservation_in_db is not None
        assert reservation_in_db.title == reservation_data["title"]
    
    def test_update_reservation(self, client: TestClient, auth_headers, seed_test_data):
        """Test updating a reservation."""
        # Get a reservation ID from the seed data
        reservation_id = seed_test_data["reservations"][0].id
        
        # Update data
        update_data = {
            "title": "Updated Reservation Title",
            "description": "Updated by API test",
            "status": ReservationStatus.APROVADA.value
        }
        
        response = client.put(f"/api/reservations/{reservation_id}", json=update_data, headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        updated_reservation = response.json()
        assert updated_reservation["id"] == reservation_id
        assert updated_reservation["title"] == update_data["title"]
        assert updated_reservation["status"] == update_data["status"]
    
    def test_delete_reservation(self, client: TestClient, auth_headers, db_session, seed_test_data):
        """Test deleting a reservation."""
        # Create a reservation to delete
        from app.services.reservation_service import ReservationService
        
        reservation_service = ReservationService(db_session)
        room_id = seed_test_data["rooms"][0].id
        user_id = seed_test_data["users"][0].id
        
        # Define time period for the reservation
        now = datetime.now()
        start_datetime = now + timedelta(days=5)
        end_datetime = start_datetime + timedelta(hours=1)
        
        # Reservation data for creation
        reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": "Reservation to Delete",
            "description": "Reservation to be deleted by API test",
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "status": ReservationStatus.PENDENTE.value
        }
        
        # Create reservation
        new_reservation = reservation_service.create_reservation(reservation_data)
        reservation_id = new_reservation.id
        
        # Delete the reservation
        response = client.delete(f"/api/reservations/{reservation_id}", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        
        # Verify reservation was deleted
        deleted_reservation = reservation_service.get_reservation_by_id(reservation_id)
        assert deleted_reservation is None
    
    def test_get_user_reservations(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting reservations for a specific user."""
        # Get a user ID from the seed data
        user_id = seed_test_data["users"][0].id
        
        response = client.get(f"/api/users/{user_id}/reservations", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        user_reservations = response.json()
        assert isinstance(user_reservations, list)
        
        # All returned reservations should be for the specified user
        for reservation in user_reservations:
            assert reservation["user_id"] == user_id
    
    def test_get_room_reservations(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting reservations for a specific room."""
        # Get a room ID from the seed data
        room_id = seed_test_data["rooms"][0].id
        
        response = client.get(f"/api/rooms/{room_id}/reservations", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        room_reservations = response.json()
        assert isinstance(room_reservations, list)
        
        # All returned reservations should be for the specified room
        for reservation in room_reservations:
            assert reservation["room_id"] == room_id
    
    def test_approve_reservation(self, client: TestClient, auth_headers, db_session, seed_test_data):
        """Test approving a reservation."""
        # Create a pending reservation
        from app.services.reservation_service import ReservationService
        
        reservation_service = ReservationService(db_session)
        room_id = seed_test_data["rooms"][0].id
        user_id = seed_test_data["users"][0].id
        
        # Define time period for the reservation
        now = datetime.now()
        start_datetime = now + timedelta(days=7)
        end_datetime = start_datetime + timedelta(hours=1)
        
        # Reservation data for creation
        reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": "Reservation to Approve",
            "description": "Reservation to be approved by API test",
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "status": ReservationStatus.PENDENTE.value
        }
        
        # Create reservation
        new_reservation = reservation_service.create_reservation(reservation_data)
        reservation_id = new_reservation.id
        
        # Approve the reservation
        response = client.put(f"/api/reservations/{reservation_id}/approve", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        approved_reservation = response.json()
        assert approved_reservation["id"] == reservation_id
        assert approved_reservation["status"] == ReservationStatus.APROVADA.value
        
        # Verify reservation status was updated in the database
        updated_reservation = reservation_service.get_reservation_by_id(reservation_id)
        assert updated_reservation.status == ReservationStatus.APROVADA
