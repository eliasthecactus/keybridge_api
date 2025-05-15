from flask_jwt_extended import jwt_required
from flask import Blueprint, request, render_template_string
from services.response_service import make_response
from models import db, LocalUsers
import bcrypt
from services.logger import loggie
from services.auth_service import register_user


setup_bp = Blueprint("setup", __name__)


@setup_bp.route('/', methods=['POST'])
def create_admin_user():
    """Creates a default admin user if no users exist, with a user-defined password."""
    """Register a new user"""
    try:
        data = request.get_json()
        response = register_user(data, initial=True)
        return make_response(**response)
    except Exception as e:
        return make_response(code=50, message=f"Unexpected error: {str(e)}", status_code=500)
