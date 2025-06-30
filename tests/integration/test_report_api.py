"""
Integration tests for report generation API endpoints.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestReportAPI:
    """Integration tests for report generation API endpoints."""
    
    def test_usage_report(self, client: TestClient, auth_headers, seed_test_data):
        """Test generating a usage report."""
        # Define date range for the report
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        response = client.get(
            "/api/reports/usage",
            params={
                "start_date": start_date,
                "end_date": end_date
            },
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        report = response.json()
        assert "total_reservations" in report
        assert "total_hours" in report
        assert "most_used_rooms" in report
        assert "start_date" in report
        assert "end_date" in report
    
    def test_occupancy_report(self, client: TestClient, auth_headers, seed_test_data):
        """Test generating an occupancy report."""
        # Define date range for the report
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        response = client.get(
            "/api/reports/occupancy",
            params={
                "start_date": start_date,
                "end_date": end_date
            },
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        report = response.json()
        assert "occupancy_rate" in report
        assert "room_utilization" in report
        assert "peak_hours" in report
        assert isinstance(report["room_utilization"], list)
    
    def test_department_usage_report(self, client: TestClient, auth_headers, seed_test_data):
        """Test generating a department usage report."""
        # Get a department ID from seed data
        department_id = seed_test_data["departments"][0].id
        
        # Define date range for the report
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        response = client.get(
            "/api/reports/department-usage",
            params={
                "department_id": department_id,
                "start_date": start_date,
                "end_date": end_date
            },
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        report = response.json()
        assert "department_id" in report
        assert "department_name" in report
        assert "total_reservations" in report
        assert "total_hours" in report
        assert report["department_id"] == department_id
    
    def test_user_activity_report(self, client: TestClient, auth_headers, seed_test_data):
        """Test generating a user activity report."""
        # Get a user ID from seed data
        user_id = seed_test_data["users"][0].id
        
        # Define date range for the report
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        response = client.get(
            "/api/reports/user-activity",
            params={
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date
            },
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        report = response.json()
        assert "user_id" in report
        assert "user_name" in report
        assert "total_reservations" in report
        assert "total_hours" in report
        assert "most_used_rooms" in report
        assert report["user_id"] == user_id
    
    def test_maintenance_report(self, client: TestClient, auth_headers, seed_test_data):
        """Test generating a maintenance report."""
        response = client.get("/api/reports/maintenance", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        report = response.json()
        assert "rooms_in_maintenance" in report
        assert "scheduled_maintenance" in report
        assert "maintenance_history" in report
        assert isinstance(report["rooms_in_maintenance"], list)
    
    def test_statistics_report(self, client: TestClient, auth_headers, seed_test_data):
        """Test getting general statistics."""
        response = client.get("/api/reports/statistics", headers=auth_headers)
        
        # Check response
        assert response.status_code == 200
        stats = response.json()
        assert "total_users" in stats
        assert "total_rooms" in stats
        assert "total_departments" in stats
        assert "total_reservations" in stats
        assert "active_reservations" in stats
        assert "reservations_today" in stats
        assert "occupancy_rate" in stats
        
        # Verify data types
        assert isinstance(stats["total_users"], int)
        assert isinstance(stats["total_rooms"], int)
        assert isinstance(stats["total_departments"], int)
        assert isinstance(stats["total_reservations"], int)
        assert isinstance(stats["active_reservations"], int)
        assert isinstance(stats["reservations_today"], int)
        assert isinstance(stats["occupancy_rate"], (int, float))
    
    def test_export_report(self, client: TestClient, auth_headers):
        """Test exporting a report in different formats."""
        # Test CSV export
        response = client.get(
            "/api/reports/export",
            params={
                "report_type": "usage",
                "format": "csv",
                "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        
        # Test Excel export
        response = client.get(
            "/api/reports/export",
            params={
                "report_type": "occupancy",
                "format": "excel",
                "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
        
        # Test PDF export
        response = client.get(
            "/api/reports/export",
            params={
                "report_type": "statistics",
                "format": "pdf"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
    
    def test_report_date_validation(self, client: TestClient, auth_headers):
        """Test report date validation."""
        # Test invalid date format
        response = client.get(
            "/api/reports/usage",
            params={
                "start_date": "invalid-date",
                "end_date": "2023-12-31"
            },
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Test start date after end date
        response = client.get(
            "/api/reports/usage",
            params={
                "start_date": "2023-12-31",
                "end_date": "2023-01-01"
            },
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Test future dates
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        response = client.get(
            "/api/reports/usage",
            params={
                "start_date": future_date,
                "end_date": future_date
            },
            headers=auth_headers
        )
        # This might be allowed depending on business rules
        # assert response.status_code in [200, 400]
    
    def test_report_filtering(self, client: TestClient, auth_headers, seed_test_data):
        """Test report filtering by various parameters."""
        # Test filtering by department
        department_id = seed_test_data["departments"][0].id
        response = client.get(
            "/api/reports/usage",
            params={
                "department_id": department_id,
                "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Test filtering by room
        room_id = seed_test_data["rooms"][0].id
        response = client.get(
            "/api/reports/usage",
            params={
                "room_id": room_id,
                "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Test filtering by user
        user_id = seed_test_data["users"][0].id
        response = client.get(
            "/api/reports/usage",
            params={
                "user_id": user_id,
                "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            },
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_report_pagination(self, client: TestClient, auth_headers):
        """Test report pagination for large datasets."""
        response = client.get(
            "/api/reports/usage",
            params={
                "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
                "limit": 10,
                "offset": 0
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        report = response.json()
        
        # Check pagination metadata
        if "pagination" in report:
            assert "total" in report["pagination"]
            assert "limit" in report["pagination"]
            assert "offset" in report["pagination"]
    
    def test_report_caching(self, client: TestClient, auth_headers):
        """Test report caching behavior."""
        params = {
            "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # First request
        response1 = client.get("/api/reports/usage", params=params, headers=auth_headers)
        assert response1.status_code == 200
        
        # Second request (should be faster if cached)
        response2 = client.get("/api/reports/usage", params=params, headers=auth_headers)
        assert response2.status_code == 200
        
        # Results should be identical
        assert response1.json() == response2.json()
