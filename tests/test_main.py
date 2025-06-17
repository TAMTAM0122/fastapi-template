from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.common.security import get_password_hash

# Use a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def db_session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_create_user(client):
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert data["is_active"] is True

def test_read_user(client, db_session):
    hashed_password = get_password_hash("password123")
    user = User(email="read@example.com", hashed_password=hashed_password)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # First, get a token for authentication
    login_response = client.post(
        "/token",
        data={"username": "read@example.com", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "read@example.com"
    assert data["id"] == user.id

def test_read_users(client, db_session):
    hashed_password = get_password_hash("password123")
    user1 = User(email="user1@example.com", hashed_password=hashed_password)
    user2 = User(email="user2@example.com", hashed_password=hashed_password)
    db_session.add_all([user1, user2])
    db_session.commit()

    # First, get a token for authentication
    login_response = client.post(
        "/token",
        data={"username": "user1@example.com", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(d["email"] == "user1@example.com" for d in data)
    assert any(d["email"] == "user2@example.com" for d in data)

def test_login_for_access_token(client, db_session):
    hashed_password = get_password_hash("securepassword")
    user = User(email="login@example.com", hashed_password=hashed_password)
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/token",
        data={"username": "login@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    response = client.post(
        "/token",
        data={"username": "nonexistent@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
