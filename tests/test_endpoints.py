"""Unit tests for the High School Management System API endpoints.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and conditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that activities endpoint returns 200 status."""
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that activities endpoint returns a dictionary."""
        # Act
        response = client.get("/activities")
        
        # Assert
        assert isinstance(response.json(), dict)

    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields."""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_contains_known_activities(self, client):
        """Test that API contains expected activities."""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity in expected_activities:
            assert activity in activities, f"Expected activity '{activity}' not found"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Test successful signup for an activity."""
        # Arrange
        email = "test@mergington.edu"
        activity = "Soccer Team"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404."""
        # Arrange
        email = "test@mergington.edu"
        activity = "Non-Existent Activity"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email(self, client):
        """Test that duplicate signup returns 400."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds participant to activity."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Basketball Club"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        check_response = client.get("/activities")
        final_count = len(check_response.json()[activity]["participants"])
        
        # Assert
        assert response.status_code == 200
        assert final_count == initial_count + 1
        assert email in check_response.json()[activity]["participants"]

    def test_signup_updates_availability(self, client):
        """Test that signup updates availability count."""
        # Arrange
        email = "another@mergington.edu"
        activity = "Art Club"
        initial_response = client.get("/activities")
        activity_data = initial_response.json()[activity]
        initial_spots = activity_data["max_participants"] - len(activity_data["participants"])
        
        # Act
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        final_response = client.get("/activities")
        activity_data = final_response.json()[activity]
        final_spots = activity_data["max_participants"] - len(activity_data["participants"])
        
        # Assert
        assert final_spots == initial_spots - 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client):
        """Test successful unregister from an activity."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404."""
        # Arrange
        email = "test@mergington.edu"
        activity = "Non-Existent Activity"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregister from activity user is not in returns 400."""
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Soccer Team"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant."""
        # Arrange
        email = "daniel@mergington.edu"
        activity = "Chess Club"
        check_response = client.get("/activities")
        assert email in check_response.json()[activity]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        final_response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert email not in final_response.json()[activity]["participants"]

    def test_unregister_updates_availability(self, client):
        """Test that unregister updates availability count."""
        # Arrange
        email = "john@mergington.edu"
        activity = "Gym Class"
        initial_response = client.get("/activities")
        activity_data = initial_response.json()[activity]
        initial_spots = activity_data["max_participants"] - len(activity_data["participants"])
        
        # Act
        client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        final_response = client.get("/activities")
        activity_data = final_response.json()[activity]
        final_spots = activity_data["max_participants"] - len(activity_data["participants"])
        
        # Assert
        assert final_spots == initial_spots + 1


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister workflows."""

    def test_signup_then_unregister_flow(self, client):
        """Test complete signup and unregister flow."""
        # Arrange
        email = "integration@mergington.edu"
        activity = "Debate Team"
        initial = client.get("/activities").json()[activity]["participants"]
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        after_signup = client.get("/activities").json()[activity]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        final = client.get("/activities").json()[activity]["participants"]
        
        # Assert
        assert email not in initial
        assert signup_response.status_code == 200
        assert email in after_signup
        assert unregister_response.status_code == 200
        assert email not in final
