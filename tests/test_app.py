import src.app as app_module
from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def activities_data():
    return {
        "Chess Club": {
            "description": "A test activity",
            "schedule": "Fridays",
            "max_participants": 3,
            "participants": ["current@example.com"],
        }
    }


@pytest.fixture
def client(monkeypatch, activities_data):
    monkeypatch.setattr(app_module, "activities", activities_data)
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_root_redirects_to_activity_page(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client, activities_data):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities_data


def test_signup_adds_participant(client, activities_data):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities_data["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client, activities_data):
    # Arrange
    email = "current@example.com"
    original_participants = activities_data["Chess Club"]["participants"].copy()

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert activities_data["Chess Club"]["participants"] == original_participants


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post("/activities/Unknown/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_removes_participant(client, activities_data):
    # Arrange
    email = "current@example.com"

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities_data["Chess Club"]["participants"]


def test_unregister_rejects_missing_participant(client, activities_data):
    # Arrange
    email = "missing@example.com"
    original_participants = activities_data["Chess Club"]["participants"].copy()

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert activities_data["Chess Club"]["participants"] == original_participants


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "current@example.com"

    # Act
    response = client.delete("/activities/Unknown/signup", params={"email": email})

    # Assert
    assert response.status_code == 404