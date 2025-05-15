from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.auth_service import role_required
from services.response_service import make_response
from services.access_service import add_access_right, get_access_rights, delete_access_right
from services.logger import loggie

access_bp = Blueprint("access", __name__)

@access_bp.route("/", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def add_access():
    """Add access rights"""
    try:
        data = request.get_json()
        result = add_access_right(data)
        return make_response(**result)
    except Exception as e:
        loggie.error(f"Unexpected error in access addition: {str(e)}")
        return make_response(code=70, message="An unexpected error occurred", status_code=500)

@access_bp.route("/", methods=["GET"])
@jwt_required()
@role_required(["admin"])
def retrieve_access_rights():
    """Retrieve access rights"""
    try:
        result = get_access_rights(request.args)
        return make_response(**result)
    except Exception as e:
        loggie.error(f"Unexpected error retrieving access rights: {str(e)}")
        return make_response(code=70, message="An unexpected error occurred", status_code=500)

@access_bp.route("/<int:access_id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def remove_access(access_id):
    """Delete an access right"""
    try:
        result = delete_access_right(access_id)
        return make_response(**result)
    except Exception as e:
        loggie.error(f"Unexpected error deleting access right: {str(e)}")
        return make_response(code=70, message="An unexpected error occurred", status_code=500)