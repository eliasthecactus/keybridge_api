from flask import Blueprint, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from services.auth_service import token_creator, role_required, jwt_decoder, login_user, register_user, change_user_password
from services.response_service import make_response
from services.logger import loggie
import json

auth_bp = Blueprint("auth", __name__)



@auth_bp.route('/register', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        response = register_user(data)
        return make_response(**response)
    except Exception as e:
        return make_response(code=50, message=f"Unexpected error: {str(e)}", status_code=500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        response = login_user(data)
        return make_response(**response)
    except Exception as e:
        return make_response(code=50, message=f"Unexpected error: {str(e)}", status_code=500)

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Allow authenticated users to change their own password.
    """
    try:
        identity = get_jwt_identity()
        json_identity = json.loads(identity)

        data = request.get_json()
        response = change_user_password(json_identity["id"], data)
        return make_response(**response)

    except Exception as e:
        return make_response(code=70, message=f"Unexpected error: {str(e)}", status_code=500)


