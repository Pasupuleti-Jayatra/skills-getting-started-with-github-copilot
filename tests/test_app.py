import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_redirect(client):
    """Test that root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    # Check if we have some activities
    assert len(activities) > 0
    # Verify activity structure
    for name, details in activities.items():
        assert isinstance(name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details

def test_signup_for_activity(client):
    """Test signing up for an activity"""
    # Get the first activity name
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    # Try signing up a new student
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    # Verify the student was added
    updated_activities = client.get("/activities").json()
    assert email in updated_activities[activity_name]["participants"]

def test_signup_duplicate(client):
    """Test that a student can't sign up twice"""
    # Get the first activity name and an existing participant
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    existing_participant = activities[activity_name]["participants"][0]
    
    # Try signing up the same student again
    response = client.post(f"/activities/{activity_name}/signup?email={existing_participant}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity(client):
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/nonexistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity(client):
    """Test unregistering from an activity"""
    # Get the first activity name and an existing participant
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    existing_participant = activities[activity_name]["participants"][0]
    
    # Unregister the participant
    response = client.post(f"/activities/{activity_name}/unregister?email={existing_participant}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {existing_participant} from {activity_name}"
    
    # Verify the student was removed
    updated_activities = client.get("/activities").json()
    assert existing_participant not in updated_activities[activity_name]["participants"]

def test_unregister_not_registered(client):
    """Test unregistering a student who isn't registered"""
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    response = client.post(f"/activities/{activity_name}/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity(client):
    """Test unregistering from a non-existent activity"""
    response = client.post("/activities/nonexistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()