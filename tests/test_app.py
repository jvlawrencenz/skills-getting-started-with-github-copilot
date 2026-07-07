import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Arrange
    data_file = tmp_path / "activities.json"
    monkeypatch.setattr(app_module, "DATA_FILE", data_file)
    app_module.activities = app_module.load_activities()

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    # No special setup needed beyond the fixture.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"]


def test_signup_for_activity_succeeds(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Chess Club"
    }
    assert email in app_module.activities["Chess Club"]["participants"]


def test_duplicate_signup_is_rejected(client):
    # Arrange
    email = "newstudent@mergington.edu"
    client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
