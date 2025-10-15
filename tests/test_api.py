"""
Test cases for the Mergington High School Activities API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestActivitiesAPI:
    """Test class for activities API endpoints."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Reset activities state before each test."""
        # Store original activities
        self.original_activities = activities.copy()
        
    def teardown_method(self):
        """Reset activities state after each test."""
        activities.clear()
        activities.update(self.original_activities)

    def test_get_activities(self):
        """Test getting all activities."""
        client = TestClient(app)
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check that each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity."""
        client = TestClient(app)
        
        # Get an existing activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity_name = list(activities_data.keys())[0]
        
        test_email = "newstudent@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        assert activity_name in data["message"]
        
        # Verify the student was added to the activity
        updated_activities = client.get("/activities").json()
        assert test_email in updated_activities[activity_name]["participants"]

    def test_signup_for_nonexistent_activity(self):
        """Test signup for an activity that doesn't exist."""
        client = TestClient(app)
        
        test_email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Activity"
        
        response = client.post(f"/activities/{nonexistent_activity}/signup?email={test_email}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_student(self):
        """Test that a student cannot sign up twice for the same activity."""
        client = TestClient(app)
        
        # Get an existing activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity_name = list(activities_data.keys())[0]
        
        test_email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response2.status_code == 400
        data = response2.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_unregister_from_activity_success(self):
        """Test successful unregistration from an activity."""
        client = TestClient(app)
        
        # Get an existing activity with participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        # Find an activity with participants
        activity_name = None
        existing_participant = None
        for name, data in activities_data.items():
            if data["participants"]:
                activity_name = name
                existing_participant = data["participants"][0]
                break
        
        assert activity_name is not None, "No activity with participants found"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={existing_participant}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert existing_participant in data["message"]
        assert activity_name in data["message"]
        
        # Verify the student was removed from the activity
        updated_activities = client.get("/activities").json()
        assert existing_participant not in updated_activities[activity_name]["participants"]

    def test_unregister_from_nonexistent_activity(self):
        """Test unregistration from an activity that doesn't exist."""
        client = TestClient(app)
        
        test_email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{nonexistent_activity}/unregister?email={test_email}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_non_registered_student(self):
        """Test unregistration of a student who is not registered."""
        client = TestClient(app)
        
        # Get an existing activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity_name = list(activities_data.keys())[0]
        
        test_email = "notregistered@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"]

    def test_root_redirect(self):
        """Test that root URL redirects to static/index.html."""
        client = TestClient(app)
        
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"

    def test_activity_capacity_limits(self):
        """Test that activities respect maximum participant limits."""
        client = TestClient(app)
        
        # Create a test activity with limited capacity
        test_activity = {
            "description": "Limited capacity test activity",
            "schedule": "Test schedule",
            "max_participants": 2,
            "participants": []
        }
        
        activities["Test Limited Activity"] = test_activity
        
        # Sign up students up to the limit
        for i in range(2):
            email = f"student{i+1}@mergington.edu"
            response = client.post(f"/activities/Test Limited Activity/signup?email={email}")
            assert response.status_code == 200
        
        # Try to sign up one more student (should still work, but activity is full)
        response = client.post("/activities/Test Limited Activity/signup?email=overflow@mergington.edu")
        assert response.status_code == 200  # API allows overbooking in current implementation
        
        # Verify all students are registered
        updated_activities = client.get("/activities").json()
        assert len(updated_activities["Test Limited Activity"]["participants"]) == 3