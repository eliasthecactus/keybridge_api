from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.client.client_launch_service import check_launch_request, process_launch
from services.response_service import make_response
from services.auth_service import role_required
import json

# Define Blueprint
client_launch_bp = Blueprint("client_launch", __name__, url_prefix="/api/client/launch")

@client_launch_bp.route('/<int:aogi_id>/check', methods=['GET'])
@jwt_required()
@role_required(['client'])
def launch_request_check(aogi_id):
    """
    Check if the client has access to launch a specific application option group item.
    """
    try:
        identity = get_jwt_identity()
        json_identiy = json.loads(identity)
        response = check_launch_request(aogi_id, json_identiy)
        return make_response(**response)
    except Exception as e:
        return make_response(code=70, message=f"Unexpected error: {str(e)}", status_code=500)

@client_launch_bp.route('/<int:aogi_id>', methods=['POST'])
@jwt_required()
@role_required(['client'])
def launch(aogi_id):
    """
    Process application launch request.
    """
    try:
        identity = get_jwt_identity()
        json_identiy = json.loads(identity)
        data = request.get_json()
        response = process_launch(aogi_id, json_identiy, data)
        return make_response(**response)
    except Exception as e:
        return make_response(code=70, message=f"Unexpected error: {str(e)}", status_code=500)