from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.limiter import limiter
from services.client.client_auth_service import authenticate_client, authenticate_client_twofa
from services.response_service import make_response
from services.auth_service import role_required
from models import db, TwoFaSources
from services.twofa_service import validate_twofa

# Initialize Blueprint
client_auth_bp = Blueprint("client_auth", __name__)


@client_auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def client_login():
    """
    Handle client login via multiple authentication sources.
    """
    try:
        # Get request data
        data = request.get_json()
        response = authenticate_client(data)
        return make_response(**response)

    except Exception as e:
        return make_response(code=70, message=f"Failed to login: {str(e)}", status_code=500)
    
@client_auth_bp.route('/login/twofa', methods=['POST'])
@limiter.limit("5 per minute")
@jwt_required()
@role_required(['client_semi'])
def client_login_2fa():
    """
    Handle client two confirmation
    """
    try:
        data = request.get_json()
        response = authenticate_client_twofa(data, identity=get_jwt_identity())
        return make_response(**response)

    except Exception as e:
        return make_response(code=70, message=f"Failed to login: {str(e)}", status_code=500)