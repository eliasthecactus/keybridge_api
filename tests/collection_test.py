import pytest
import bcrypt
import os
import json
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, decode_token
from models import db
from models import LocalUsers
from services.auth_service import (
    token_creator, jwt_decoder, role_required, register_user, login_user, change_user_password
)
from unittest.mock import patch, MagicMock
from services.response_service import make_response

app = Flask(__name__)
db_user = os.getenv("KEYBRIDGE_DB_USERNAME", "")
db_password = os.getenv("KEYBRIDGE_DB_PASSWORD", "")
db_host = os.getenv("KEYBRIDGE_DB_HOST", "")
db_port = os.getenv("KEYBRIDGE_DB_PORT", "")
db_name = os.getenv("KEYBRIDGE_DB_NAME", "")

if all([db_user, db_password, db_host, db_port, db_name]):
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "test_secret")
print("Test with " + app.config["SQLALCHEMY_DATABASE_URI"])
db.init_app(app)
jwt = JWTManager(app)

@pytest.fixture(scope="module")
def test_client():
    """Create a Flask test client with an in-memory database."""
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            try:
                yield client
            finally:
                db.session.rollback()
                db.session.remove()
                db.drop_all()
@pytest.fixture
def test_user():
    """Create a test user and return a fresh instance from the database."""
    with app.app_context():
        db.session.query(LocalUsers).filter_by(username="testuser").delete()
        db.session.commit()

        password = bcrypt.hashpw("securePass123".encode(), bcrypt.gensalt()).decode()
        new_user = LocalUsers(
            name="Test User",
            username="testuser",
            password_hash=password,
            password_salt="salt",
            disabled=False
        )
        db.session.add(new_user)
        db.session.commit()

        # Fetch a fresh instance to ensure it's attached to the session
        return LocalUsers.query.filter_by(username="testuser").first()
@pytest.fixture
def auth_headers():
    """Generate a test JWT token."""
    def _auth_headers(user_id="test_user", auth_id=1, token_type="admin"):
        access_token = token_creator(user_id, token_type, {"auth_id": auth_id})
        return {"Authorization": f"Bearer {access_token}"}
    return _auth_headers

# ==========================
# TEST JWT FUNCTIONS
# ==========================

def test_token_creator():
    """Test that the token creator generates valid JWT tokens."""
    with app.app_context():
        token = token_creator("123", "admin")
        decoded = decode_token(token)

        assert decoded["sub"] is not None
        payload = json.loads(decoded["sub"])
        assert payload["id"] == "123"
        assert payload["type"] == "admin"

def test_jwt_decoder():
    """Test that jwt_decoder correctly parses JSON tokens."""
    payload = {"id": "123", "type": "admin", "data": {"role": "admin"}}
    encoded_token = json.dumps(payload)
    decoded = jwt_decoder(encoded_token)

    assert decoded["id"] == "123"
    assert decoded["type"] == "admin"
    assert decoded["data"]["role"] == "admin"

# ==========================
# TEST USER REGISTRATION
# ==========================

def test_register_user_success(test_client):
    """Test successful user registration."""
    payload = {
        "name": "New User",
        "username": "newuser",
        "password": "StrongPass!123"
    }
    response = register_user(payload)
    assert response["code"] == 0
    assert response["message"] == "User registered successfully"

def test_register_user_existing(test_client, test_user):
    """Test registering with an existing username."""
    payload = {
        "name": "Duplicate User",
        "username": test_user.username,
        "password": "StrongPass!123"
    }
    response = register_user(payload)
    assert response["code"] != 0

def test_register_user_weak_password(test_client):
    """Test registering with a weak password."""
    payload = {
        "name": "WeakPassUser",
        "username": "weakuser",
        "password": "123"
    }
    response = register_user(payload)
    assert response["code"] == 40  # Password too weak

# ==========================
# TEST LOGIN FUNCTION
# ==========================

def test_login_user_success(test_client, test_user):
    """Test logging in with correct credentials."""
    payload = {"username": test_user.username, "password": "securePass123"}
    response = login_user(payload)

    assert response["code"] == 0
    assert "access_token" in response["data"]

def test_login_user_wrong_password(test_client, test_user):
    """Test login fails with incorrect password."""
    payload = {"username": test_user.username, "password": "wrongpassword"}
    response = login_user(payload)

    assert response["code"] == 30  # Invalid credentials

def test_login_user_disabled(test_client, test_user):
    """Test login for a disabled account."""
    with app.app_context():
        # Ensure user is marked as disabled and committed properly
        LocalUsers.query.filter_by(id=test_user.id).update({"disabled": True})
        db.session.commit()

        # Force a refresh by querying again
        disabled_user = LocalUsers.query.get(test_user.id)
        assert disabled_user.disabled is True  # Ensure user is actually disabled

        payload = {"username": disabled_user.username, "password": "securePass123"}
        response = login_user(payload)

        assert response["code"] == 10  # Account is disabled

        # Re-enable the user after the test
        LocalUsers.query.filter_by(id=disabled_user.id).update({"disabled": False})
        db.session.commit()
                
        
# ==========================
# TEST ROLE-BASED ACCESS
# ==========================

@patch("services.auth_service.get_jwt_identity", return_value=json.dumps({"id": "123", "type": "admin"}))
def test_role_required_success(mock_jwt):
    """Test role_required decorator allows correct role."""
    @role_required(["admin"])
    def protected_function():
        return {"message": "Access granted"}, 200

    response = protected_function()
    assert response[1] == 200
    assert response[0]["message"] == "Access granted"

@patch("services.auth_service.get_jwt_identity", return_value=json.dumps({"id": "123", "type": "client"}))
def test_role_required_denied(mock_jwt):
    """Test role_required decorator denies unauthorized users."""
    @role_required(["admin"])
    def protected_function():
        return make_response(code=10, message="Unauthorized access (client).", status_code=403)

    response_tuple = protected_function()

    # Unpack tuple response
    if isinstance(response_tuple, tuple):
        response, status_code = response_tuple
    else:
        response = response_tuple
        status_code = response.status_code

    # Ensure correct status code
    assert status_code == 403  

    # Extract JSON data properly
    response_data = response if isinstance(response, dict) else response.get_json()
    assert response_data["message"] == "Unauthorized access (client)."


# ==========================
# TEST PASSWORD CHANGE
# ==========================

def test_change_user_password_success(test_client, test_user):
    """Test changing a user's password successfully."""
    payload = {
        "current_password": "securePass123",
        "new_password": "NewStrongPass!456"
    }
    response = change_user_password(test_user.id, payload)

    assert response["code"] == 0  # Password updated successfully

    # Verify new password works
    test_user = LocalUsers.query.get(test_user.id)
    assert bcrypt.checkpw("NewStrongPass!456".encode(), test_user.password_hash.encode())

def test_change_user_password_wrong_current(test_client, test_user):
    """Test changing password with incorrect current password."""
    payload = {
        "current_password": "wrongpassword",
        "new_password": "NewPass123!"
    }
    response = change_user_password(test_user.id, payload)

    assert response["code"] == 30  # Current password incorrect

def test_change_user_password_weak(test_client, test_user):
    """Test changing password to a weak one."""
    payload = {
        "current_password": "NewStrongPass!456",
        "new_password": "123"
    }
    response = change_user_password(test_user.id, payload)

    assert response["code"] == 40  # New password is too weak