from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.client.client_access_service import get_requestable_applications, create_access_request
from services.response_service import make_response
from services.auth_service import role_required
import json

# Define Blueprint
client_access_bp = Blueprint("client_access", __name__)

@client_access_bp.route('/request', methods=['GET', 'POST'])
@jwt_required()
@role_required(['client'])
def client_requestable_applications():
    """
    Handle application access requests for the client.
    - GET: Retrieve requestable applications.
    - POST: Request access to an application.
    """
    json_identity = json.loads(get_jwt_identity())
    try:
        if request.method == 'POST':
            return create_access_request(request.get_json(), json_identity)

        return get_requestable_applications(json_identity)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return make_response(code=70, message="An unexpected error occurred", status_code=500)