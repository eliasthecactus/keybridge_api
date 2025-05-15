from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.client.client_application_service import get_client_applications
from services.response_service import make_response
from services.auth_service import role_required
import json

# Initialize Blueprint
client_application_bp = Blueprint("client_application", __name__)

@client_application_bp.route('/', methods=['GET'])
@jwt_required()
@role_required(['client'])
def client_get_applications():
    """
    Fetch applications the client has access to.
    """
    try:
        identity = get_jwt_identity()
        json_identiy = json.loads(identity)
        response = get_client_applications(json_identiy)
        return make_response(**response)

    except Exception as e:
        return make_response(code=70, message=f"Unexpected error: {str(e)}", status_code=500)