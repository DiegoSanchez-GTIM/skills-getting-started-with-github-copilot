"""Unit tests for the High School Management System API endpoints."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that activities endpoint returns 200 status."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that activities endpoint returns a dictionary."""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_contains_known_activities(self, client):
        """Test that API contains expected activities."""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in expected_activities:
            assert activity in activities


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404."""
        response = client.post(
            "/activities/Non-Existent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email(self, client):
        """Test that duplicate signup returns 400."""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Try to sign up with an email already in the activity
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds participant to activity."""
        email = "newstudent@mergington.edu"
        activity = "Basketball Club"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        check_response = client.get("/activities")
        final_count = len(check_response.json()[activity]["participants"])
        assert final_count == initial_count + 1
        assert email in check_response.json()[activity]["participants"]

    def test_signup_updates_availability(self, client):
        """Test that signup updates availability count."""
        email = "another@mergington.edu"
        activity = "Art Club"
        
        # Get initial availability
        initial_response = client.get("/activities")
        activity_data = initial_response.json()[activity]
        initial_spots = activity_data["max_participants"] - len(activity_data["participants"])
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Check new availability
        final_response = client.get("/activities")
        activity_data = final_response.json()[activity]
        final_spots = activity_data["max_participants"] - len(activity_data["participants"])
        assert final_spots == initial_spots - 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client):
        """Test successful unregister from an activity."""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Non-Existent Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregister from activity user is not in returns 400."""
        response = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant."""
        email = "daniel@mergington.edu"
        activity = "Chess Club"
        
        # Verify participant exists before unregister
        check_response = client.get("/activities")
        assert email in check_response.json()[activity]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity]["participants"]

    def test_unregister_updates_availability(self, client):
        """Test that unregister updates availability count."""
        email = "john@mergington.edu"
        activity = "Gym Class"
        
        # Get initial availability
        initial_response = client.get("/activities")
        activity_data = initial_response.json()[activity]
        initial_spots = activity_data["max_participants"] - len(activity_data["participants"])
        
        # Unregister
        client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Check new availability
        final_response = client.get("/activities")
        activity_data = final_response.json()[activity]
        final_spots = activity_data["max_participants"] - len(activity_data["participants"])
        assert final_spots == initial_spots + 1


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister workflows."""

    def test_signup_then_unregister_flow(self, client):
        """Test complete signup and unregister flow."""
        email = "integration@mergington.edu"
        activity = "Debate Team"
        
        # Verify not registered initially
        initial = client.get("/activities").json()[activity]["participants"]
        assert email not in initial
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify registered
        after_signup = client.get("/activities").json()[activity]["participants"]
        assert email in after_signup
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify not registered again
        final = client.get("/activities").json()[activity]["participants"]
        assert email not in final
