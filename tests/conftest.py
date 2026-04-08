"""Test configuration and fixtures for FastAPI tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_activity_data(client):
    """Get the current activities from the API."""
    response = client.get("/activities")
    return response.json()
