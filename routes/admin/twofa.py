from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.twofa_service import create_twofa_source,get_twofa_sources,get_twofa_source,update_twofa_source,delete_twofa_source, validate_twofa
from services.response_service import make_response

twofa_bp = Blueprint("twofa", __name__)

@twofa_bp.route("/", methods=["POST"])
@jwt_required()
def add_twofa_source():
    """Endpoint to create a new 2FA source."""
    data = request.get_json()
    response = create_twofa_source(data)
    return make_response(**response)

@twofa_bp.route("/", methods=["GET"])
@jwt_required()
def fetch_twofa_sources():
    """Endpoint to retrieve all 2FA sources."""
    response = get_twofa_sources()
    return make_response(**response)

@twofa_bp.route("/<int:twofa_id>", methods=["GET"])
@jwt_required()
def fetch_twofa_source(twofa_id):
    """Endpoint to retrieve a specific 2FA source."""
    response = get_twofa_source(twofa_id)
    return make_response(**response)

@twofa_bp.route("/<int:twofa_id>", methods=["PUT"])
@jwt_required()
def modify_twofa_source(twofa_id):
    """Endpoint to update a 2FA source."""
    data = request.get_json()
    response = update_twofa_source(twofa_id, data)
    return make_response(**response)

@twofa_bp.route("/<int:twofa_id>", methods=["DELETE"])
@jwt_required()
def remove_twofa_source(twofa_id):
    """Endpoint to delete a 2FA source."""
    response = delete_twofa_source(twofa_id)
    return make_response(**response)

@twofa_bp.route("/validate", methods=["POST"])
@jwt_required()
def test_twofa_endpoint():
    data = request.get_json()
    response = validate_twofa(data)
    print(response)
    return make_response(**response)
