import json
from flask_jwt_extended import create_access_token, get_jwt_identity
from functools import wraps
from services.response_service import make_response
from services.security_service import check_password_strength
from models import db, LocalUsers
import bcrypt
from services.logger import loggie

def token_creator(user_id: str, token_type: str, data=None) -> str:
    """
    Create a JWT token with custom payload.
    """
    valid_types = {"admin", "client", "client_semi"}
    if token_type not in valid_types:
        raise ValueError(f"Invalid token type: {token_type}")

    if not user_id:
        raise ValueError("Invalid user_id")

    payload = {
        "id": user_id,
        "type": token_type,
        "data": data,
    }

    return create_access_token(identity=json.dumps(payload))

def jwt_decoder(jwt):
    """Decodes JWT payload."""
    try:
        return json.loads(jwt)
    except Exception:
        return None

def role_required(allowed_roles):
    """
    Decorator to restrict access to users with specific roles.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                decoded = jwt_decoder(get_jwt_identity())
                user_type = decoded.get("type")

                # Check if the user's role is allowed
                if user_type not in allowed_roles:
                    return make_response(code=10, message=f"Unauthorized access ({user_type}).", status_code=403)

            except Exception as e:
                return make_response(code=20, message=f"Error decoding JWT: {str(e)}", status_code=403)

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def register_user(data, initial=False):
    """Handles user registration logic."""
    try:
        if initial:
            name = "Admin"
            username = "admin"
        else:
            username = data.get('username')
            name = data.get('name')

        password = data.get('password')

        if not all([name, username, password]):
            return {"code": 30, "message": "Name, username, and password are required", "status_code": 400}
        
        if initial and len(LocalUsers.query.all()) > 0:
            return {"code": 60, "message": "There is already a local admin setup", "status_code": 400}


        if not check_password_strength(password):
            return {"code": 40, "message": "Password too weak", "status_code": 400}

        if LocalUsers.query.filter_by(username=username).first():
            return {"code": 20, "message": "Username already in use", "status_code": 400}

        # Hash password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt).decode()

        new_user = LocalUsers(
            name=name,
            username=username,
            password_hash=hashed_password,
            password_salt=salt.decode()
        )

        db.session.add(new_user)
        db.session.commit()

        loggie.info(f"User {username} registered successfully.")
        return {"code": 0, "message": "User registered successfully", "status_code": 201}

    except Exception as e:
        loggie.error(f"Unexpected error during registration: {str(e)}")
        return {"code": 50, "message": "An unexpected error occurred", "status_code": 500}

def login_user(data):
    """Handles user login logic."""
    try:
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {"code": 20, "message": "Username and password are required", "status_code": 400}

        user = LocalUsers.query.filter_by(username=username).first()
        if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return {"code": 30, "message": "Invalid credentials", "status_code": 401}

        if user.disabled:
            return {"code": 10, "message": "Account is disabled", "status_code": 403}

        # Generate JWT token
        access_token = token_creator(str(user.id), "admin")
        response_data = {
            "access_token": access_token,
            "user_id": user.id,
            "username": user.name
        }

        loggie.info(f"User {username} logged in successfully")
        return {"code": 0, "message": "Login successful", "data": response_data, "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error during login: {str(e)}")
        return {"code": 50, "message": "An unexpected error occurred", "status_code": 500}
    
def change_user_password(user_id, data):
    """Handles user password change."""
    try:
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return {"code": 30, "message": "Current and new password are required", "status_code": 400}

        if not check_password_strength(new_password):
            return {"code": 40, "message": "New password is too weak", "status_code": 400}

        user = LocalUsers.query.get(user_id)
        if not user:
            return {"code": 50, "message": "User not found", "status_code": 404}

        if not bcrypt.checkpw(current_password.encode(), user.password_hash.encode()):
            return {"code": 30, "message": "Current password is incorrect", "status_code": 401}

        # Hash new password
        salt = bcrypt.gensalt()
        hashed_new_password = bcrypt.hashpw(new_password.encode(), salt).decode()

        # Update password in the database
        user.password_hash = hashed_new_password
        user.password_salt = salt.decode()
        db.session.commit()

        loggie.info(f"User {user.username} changed their password.")
        return {"code": 0, "message": "Password updated successfully", "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error during password change: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}