"""
End-to-end tests for reservation flows.
"""

from datetime import datetime, timedelta, timezone
import pytest
import uuid
from fastapi.testclient import TestClient
from app.models.enums import ReservationStatus

@pytest.mark.e2e
class TestReservationFlow:
    """End-to-end tests for reservation management flows."""
    
    def test_complete_reservation_flow(self, client: TestClient, db_session, auth_headers):
        """Test the complete flow of creating, approving, and canceling a reservation."""
        # Step 1: Login as a user with appropriate permissions
        # (Using auth_headers fixture which already handles login)
        
        # Step 2: Browse available rooms
        # Get the current time to set future reservation dates
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        day_after_tomorrow = now + timedelta(days=2)
        
        # Format dates for API request
        start_date = tomorrow.strftime("%Y-%m-%dT%H:%M:%S")
        end_date = (tomorrow + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
        
        # Check available rooms for the time period
        response = client.get(
            "/api/rooms/available",
            params={"start_datetime": start_date, "end_datetime": end_date},
            headers=auth_headers
        )
        assert response.status_code == 200
        available_rooms = response.json()
        assert len(available_rooms) > 0
        
        # Step 3: Select a room and create a reservation
        selected_room = available_rooms[0]
        room_id = selected_room["id"]
        
        # Get user ID from auth context
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        user_data = response.json()
        user_id = user_data["id"]
        
        # Create reservation data
        reservation_title = f"E2E Test Reservation {now.strftime('%Y%m%d%H%M%S')}"
        reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": reservation_title,
            "description": "Reservation created during E2E testing",
            "start_datetime": start_date,
            "end_datetime": end_date,
            "status": ReservationStatus.PENDENTE.value
        }
        
        # Create the reservation
        response = client.post(
            "/api/reservations",
            json=reservation_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        created_reservation = response.json()
        reservation_id = created_reservation["id"]
        
        # Step 4: View the created reservation
        response = client.get(
            f"/api/reservations/{reservation_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        reservation = response.json()
        assert reservation["id"] == reservation_id
        assert reservation["title"] == reservation_title
        assert reservation["status"] == ReservationStatus.PENDENTE.value
        
        # Step 5: Admin approves the reservation
        # In a real E2E test, we would log in as admin here
        # For this test, we'll use the same auth_headers but call the approve endpoint
        
        response = client.put(
            f"/api/reservations/{reservation_id}/approve",
            headers=auth_headers
        )
        assert response.status_code == 200
        approved_reservation = response.json()
        assert approved_reservation["status"] == ReservationStatus.CONFIRMADA.value
        
        # Step 6: User views their approved reservation
        response = client.get(
            f"/api/users/{user_id}/reservations",
            headers=auth_headers
        )
        assert response.status_code == 200
        user_reservations = response.json()
        
        # Find our reservation in the list
        found_reservation = None
        for res in user_reservations:
            if res["id"] == reservation_id:
                found_reservation = res
                break
                
        assert found_reservation is not None
        assert found_reservation["status"] == ReservationStatus.CONFIRMADA.value
        
        # Step 7: User cancels the reservation
        response = client.put(
            f"/api/reservations/{reservation_id}",
            json={"status": ReservationStatus.CANCELADA.value},
            headers=auth_headers
        )
        assert response.status_code == 200
        canceled_reservation = response.json()
        assert canceled_reservation["status"] == ReservationStatus.CANCELADA.value
        
        # Step 8: Verify the room is available again for the same time slot
        response = client.get(
            "/api/rooms/available",
            params={"start_datetime": start_date, "end_datetime": end_date},
            headers=auth_headers
        )
        assert response.status_code == 200
        available_rooms_after_cancel = response.json()
        
        # Find our room in the available rooms list
        room_available_again = False
        for room in available_rooms_after_cancel:
            if room["id"] == room_id:
                room_available_again = True
                break
                
        assert room_available_again
    
    def test_reservation_conflict_handling(self, client: TestClient, db_session, auth_headers):
        """Test handling of conflicting reservations."""
        # Step 1: Create an initial reservation
        now = datetime.now()
        start_date = (now + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
        end_date = (now + timedelta(days=3, hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
        
        # Get available rooms
        response = client.get(
            "/api/rooms/available",
            params={"start_datetime": start_date, "end_datetime": end_date},
            headers=auth_headers
        )
        assert response.status_code == 200
        available_rooms = response.json()
        assert len(available_rooms) > 0
        
        # Get user ID
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        user_data = response.json()
        user_id = user_data["id"]
        
        # Create first reservation
        room_id = available_rooms[0]["id"]
        first_reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": f"First Test Reservation {now.strftime('%Y%m%d%H%M%S')}",
            "description": "First reservation for conflict testing",
            "start_datetime": start_date,
            "end_datetime": end_date,
            "status": ReservationStatus.PENDENTE.value
        }
        
        response = client.post(
            "/api/reservations",
            json=first_reservation_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        
        # Approve the first reservation
        first_reservation_id = response.json()["id"]
        response = client.put(
            f"/api/reservations/{first_reservation_id}/approve",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 2: Try to create a conflicting reservation for the same room and time
        conflicting_reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": f"Conflicting Reservation {now.strftime('%Y%m%d%H%M%S')}",
            "description": "This reservation should conflict with the first one",
            "start_datetime": start_date,
            "end_datetime": end_date,
            "status": ReservationStatus.PENDENTE.value
        }
        
        response = client.post(
            "/api/reservations",
            json=conflicting_reservation_data,
            headers=auth_headers
        )
        
        # Should be rejected due to conflict
        assert response.status_code in [400, 409]
        
        # Step 3: Verify the room is not available for the time period
        response = client.get(
            "/api/rooms/available",
            params={"start_datetime": start_date, "end_datetime": end_date},
            headers=auth_headers
        )
        assert response.status_code == 200
        available_rooms_after = response.json()
        
        # The room should not be in the available list
        room_still_available = False
        for room in available_rooms_after:
            if room["id"] == room_id:
                room_still_available = True
                break
                
        assert not room_still_available
        
        # Step 4: Create a reservation with a different time slot (should succeed)
        different_start = (now + timedelta(days=3, hours=3)).strftime("%Y-%m-%dT%H:%M:%S")
        different_end = (now + timedelta(days=3, hours=5)).strftime("%Y-%m-%dT%H:%M:%S")
        
        different_reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": f"Different Time Reservation {now.strftime('%Y%m%d%H%M%S')}",
            "description": "This reservation should not conflict with the first one",
            "start_datetime": different_start,
            "end_datetime": different_end,
            "status": ReservationStatus.PENDENTE.value
        }
        
        response = client.post(
            "/api/reservations",
            json=different_reservation_data,
            headers=auth_headers
        )
        
        # Should succeed
        assert response.status_code == 201

    def test_multi_user_reservation_flow(self, client: TestClient, db_session, auth_headers):
        """Test reservation flow with multiple users and different roles."""
        # Step 1: Create multiple reservations by different users
        now = datetime.now()
        
        # User 1 creates a reservation
        start_date_1 = (now + timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%S")
        end_date_1 = (now + timedelta(days=4, hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        
        # Get available rooms
        response = client.get(
            "/api/rooms/available",
            params={"start_datetime": start_date_1, "end_datetime": end_date_1},
            headers=auth_headers
        )
        assert response.status_code == 200
        available_rooms = response.json()
        assert len(available_rooms) > 0
        room_id = available_rooms[0]["id"]
        
        # Get current user ID
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        user_1_id = response.json()["id"]
        
        # Create first reservation
        reservation_data_1 = {
            "room_id": room_id,
            "user_id": user_1_id,
            "title": f"Multi-user Test 1 {now.strftime('%Y%m%d%H%M%S')}",
            "description": "First reservation in multi-user test",
            "start_datetime": start_date_1,
            "end_datetime": end_date_1,
            "status": ReservationStatus.PENDENTE.value
        }
        
        response = client.post(
            "/api/reservations",
            json=reservation_data_1,
            headers=auth_headers
        )
        assert response.status_code == 201
        reservation_1_id = response.json()["id"]
        
        # Step 2: Another user tries to reserve same room at different time
        start_date_2 = (now + timedelta(days=4, hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
        end_date_2 = (now + timedelta(days=4, hours=3)).strftime("%Y-%m-%dT%H:%M:%S")
        
        reservation_data_2 = {
            "room_id": room_id,
            "user_id": user_1_id,  # Same user for simplicity in this test
            "title": f"Multi-user Test 2 {now.strftime('%Y%m%d%H%M%S')}",
            "description": "Second reservation in multi-user test",
            "start_datetime": start_date_2,
            "end_datetime": end_date_2,
            "status": ReservationStatus.PENDENTE.value
        }
        
        response = client.post(
            "/api/reservations",
            json=reservation_data_2,
            headers=auth_headers
        )
        assert response.status_code == 201
        reservation_2_id = response.json()["id"]
        
        # Step 3: Approve first reservation
        response = client.put(
            f"/api/reservations/{reservation_1_id}/approve",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 4: Verify both reservations exist but only first is approved
        response = client.get(f"/api/reservations/{reservation_1_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == ReservationStatus.CONFIRMADA.value
        
        response = client.get(f"/api/reservations/{reservation_2_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == ReservationStatus.PENDENTE.value
        
        # Step 5: Approve second reservation
        response = client.put(
            f"/api/reservations/{reservation_2_id}/approve",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 6: Verify room utilization
        response = client.get(
            f"/api/rooms/{room_id}/utilization",
            params={
                "start_date": (now + timedelta(days=4)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=4)).strftime("%Y-%m-%d")
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        utilization = response.json()
        assert utilization["total_hours"] >= 3  # Both reservations total 3 hours

    def test_reservation_validation_rules(self, client: TestClient, db_session, auth_headers):
        """Test various reservation validation rules."""
        now = datetime.now()
        
        # Get user ID
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        user_id = response.json()["id"]
        
        # Get available rooms
        response = client.get(
            "/api/rooms/available",
            params={
                "start_datetime": (now + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S"),
                "end_datetime": (now + timedelta(days=5, hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        available_rooms = response.json()
        assert len(available_rooms) > 0
        room_id = available_rooms[0]["id"]
        
        # Test 1: Past date reservation (should fail)
        past_start = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        past_end = (now - timedelta(hours=23)).strftime("%Y-%m-%dT%H:%M:%S")
        
        past_reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": "Past Date Test",
            "description": "This should fail",
            "start_datetime": past_start,
            "end_datetime": past_end,
            "status": ReservationStatus.PENDENTE.value
        }
        
        response = client.post(
            "/api/reservations",
            json=past_reservation_data,
            headers=auth_headers
        )
        assert response.status_code in [400, 422]  # Should be rejected
        
        # Test 2: End time before start time (should fail)
        future_start = (now + timedelta(days=6, hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
        future_end = (now + timedelta(days=6, hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        
        invalid_time_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": "Invalid Time Test",
            "description": "End before start",
            "start_datetime": future_start,
            "end_datetime": future_end,
            "status": ReservationStatus.PENDENTE.value
        }
        
        response = client.post(
            "/api/reservations",
            json=invalid_time_data,
            headers=auth_headers
        )
        assert response.status_code in [400, 422]  # Should be rejected
        
        # Test 3: Valid reservation (should succeed)
        valid_start = (now + timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%S")
        valid_end = (now + timedelta(days=6, hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
        
        valid_reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": "Valid Reservation Test",
            "description": "This should work",
            "start_datetime": valid_start,
            "end_datetime": valid_end,
            "status": ReservationStatus.PENDENTE.value
        }
        
        response = client.post(
            "/api/reservations",
            json=valid_reservation_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        
        # Test 4: Missing required fields (should fail)
        incomplete_data = {
            "room_id": room_id,
            "title": "Incomplete Data",
            # Missing user_id, start_datetime, end_datetime
        }
        
        response = client.post(
            "/api/reservations",
            json=incomplete_data,
            headers=auth_headers
        )
        assert response.status_code in [400, 422]  # Should be rejected
        
        # Test 5: Non-existent room (should fail)
        nonexistent_room_data = {
            "room_id": 99999,  # Non-existent room ID
            "user_id": user_id,
            "title": "Non-existent Room Test",
            "description": "This should fail",
            "start_datetime": valid_start,
            "end_datetime": valid_end,
            "status": ReservationStatus.PENDENTE.value
        }
        
        response = client.post(
            "/api/reservations",
            json=nonexistent_room_data,
            headers=auth_headers
        )
        assert response.status_code in [400, 404]  # Should be rejected

    def test_reservation_reporting_flow(self, client: TestClient, db_session, auth_headers):
        """Test reservation reporting and statistics flow."""
        now = datetime.now()
        
        # Create several reservations for reporting
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        user_id = response.json()["id"]
        
        # Get available rooms
        response = client.get(
            "/api/rooms/available",
            params={
                "start_datetime": (now + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S"),
                "end_datetime": (now + timedelta(days=7, hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        available_rooms = response.json()
        assert len(available_rooms) > 0
        
        # Create multiple reservations
        reservation_ids = []
        for i in range(3):
            start_time = now + timedelta(days=7+i, hours=i)
            end_time = start_time + timedelta(hours=1)
            
            reservation_data = {
                "room_id": available_rooms[0]["id"],
                "user_id": user_id,
                "title": f"Report Test Reservation {i+1}",
                "description": f"Reservation for reporting test {i+1}",
                "start_datetime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "end_datetime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "status": ReservationStatus.PENDENTE.value
            }
            
            response = client.post(
                "/api/reservations",
                json=reservation_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            reservation_ids.append(response.json()["id"])
        
        # Approve some reservations
        for reservation_id in reservation_ids[:2]:
            response = client.put(
                f"/api/reservations/{reservation_id}/approve",
                headers=auth_headers
            )
            assert response.status_code == 200
        
        # Test usage report
        response = client.get(
            "/api/reports/usage",
            params={
                "start_date": (now + timedelta(days=7)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=10)).strftime("%Y-%m-%d")
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        usage_report = response.json()
        assert "total_reservations" in usage_report
        assert usage_report["total_reservations"] >= 3
        
        # Test user activity report
        response = client.get(
            "/api/reports/user-activity",
            params={
                "user_id": user_id,
                "start_date": (now + timedelta(days=7)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=10)).strftime("%Y-%m-%d")
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        activity_report = response.json()
        assert "user_id" in activity_report
        assert activity_report["user_id"] == user_id
        
        # Test statistics endpoint
        response = client.get("/api/reports/statistics", headers=auth_headers)
        assert response.status_code == 200
        statistics = response.json()
        assert "total_users" in statistics
        assert "total_rooms" in statistics
        assert "total_reservations" in statistics
        assert "active_reservations" in statistics
