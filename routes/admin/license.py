from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.auth_service import role_required
from services.response_service import make_response
from services.license_service import apply_license, get_license, remove_license, update_license
from services.logger import loggie
from schemas import LicenseSchema

license_bp = Blueprint("license", __name__, url_prefix="/license")
license_schema = LicenseSchema()

@license_bp.route('', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def license_server():
    """Apply a new license key."""
    try:
        data = request.get_json()
        validated_data = license_schema.load(data)

        result = apply_license(validated_data["license_key"])
        return make_response(**result)
    except Exception as e:
        loggie.error(f"Unexpected error in license application: {str(e)}")
        return make_response(code=60, message="An unexpected error occurred", data=str(e), status_code=500)


@license_bp.route('', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def fetch_license():
    """Retrieve the current license key."""
    try:
        result = get_license()
        return make_response(**result)
    except Exception as e:
        loggie.error(f"Unexpected error fetching license: {str(e)}")
        return make_response(code=60, message="An unexpected error occurred", data=str(e), status_code=500)


@license_bp.route('', methods=['DELETE'])
@jwt_required()
@role_required(['admin'])
def delete_license():
    """Delete the current license key."""
    try:
        result = remove_license()
        return make_response(**result)
    except Exception as e:
        loggie.error(f"Unexpected error deleting license: {str(e)}")
        return make_response(code=60, message="An unexpected error occurred", data=str(e), status_code=500)


@license_bp.route('', methods=['PUT'])
@jwt_required()
@role_required(['admin'])
def change_license():
    """Change the license key."""
    try:
        data = request.get_json()
        validated_data = license_schema.load(data)

        result = apply_license(validated_data["license_key"])
        return make_response(**result)
    except Exception as e:
        loggie.error(f"Unexpected error changing license: {str(e)}")
        return make_response(code=60, message="An unexpected error occurred", data=str(e), status_code=500)