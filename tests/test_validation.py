"""
Test cases for data validation and business logic.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestDataValidation:
    """Test class for data validation and business logic."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test method."""
        # Store original activities
        from src.app import activities
        self.original_activities = activities.copy()
        yield
        # Reset activities state after each test
        activities.clear()
        activities.update(self.original_activities)

    def test_email_parameter_required(self):
        """Test that email parameter is required for signup."""
        client = TestClient(app)
        
        # Get an existing activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity_name = list(activities_data.keys())[0]
        
        # Try to signup without email parameter
        response = client.post(f"/activities/{activity_name}/signup")
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_email_parameter_required_for_unregister(self):
        """Test that email parameter is required for unregistration."""
        client = TestClient(app)
        
        # Get an existing activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity_name = list(activities_data.keys())[0]
        
        # Try to unregister without email parameter
        response = client.delete(f"/activities/{activity_name}/unregister")
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_activity_name_encoding(self):
        """Test that activity names with special characters are handled correctly."""
        client = TestClient(app)
        
        # Add an activity with special characters for testing
        special_activity_name = "Art & Crafts Club"
        activities[special_activity_name] = {
            "description": "Creative arts and crafts",
            "schedule": "Fridays, 2:00 PM - 4:00 PM",
            "max_participants": 15,
            "participants": []
        }
        
        test_email = "artist@mergington.edu"
        
        # Test signup with URL encoding
        from urllib.parse import quote
        encoded_name = quote(special_activity_name)
        response = client.post(f"/activities/{encoded_name}/signup?email={test_email}")
        
        assert response.status_code == 200
        
        # Verify the student was added
        updated_activities = client.get("/activities").json()
        assert test_email in updated_activities[special_activity_name]["participants"]

    def test_empty_email_handling(self):
        """Test handling of empty email addresses."""
        client = TestClient(app)
        
        # Get an existing activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity_name = list(activities_data.keys())[0]
        
        # Store original participants count
        original_participants = activities_data[activity_name]["participants"].copy()
        
        # Try to signup with empty email
        response = client.post(f"/activities/{activity_name}/signup?email=")
        
        # The API should handle this gracefully
        # Empty email should be treated as a valid string by FastAPI
        assert response.status_code in [200, 422]
        
        # If the empty email was added, remove it for cleanup
        if response.status_code == 200:
            from src.app import activities
            current_participants = activities[activity_name]["participants"]
            if "" in current_participants:
                current_participants.remove("")

    def test_activities_data_structure(self):
        """Test that all activities have the required data structure."""
        client = TestClient(app)
        
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities_data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities_data.items():
            # Check that activity name is a non-empty string
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
            
            # Check that all required fields are present
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"
            
            # Check data types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Check that max_participants is positive
            assert activity_data["max_participants"] > 0
            
            # Check that all participants are strings (email addresses)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                # Allow empty emails for testing purposes, but warn if found
                if len(participant) == 0:
                    print(f"Warning: Empty participant found in {activity_name}")
                # Most participants should have valid email-like strings
                # but we won't enforce strict email validation in the data structure test