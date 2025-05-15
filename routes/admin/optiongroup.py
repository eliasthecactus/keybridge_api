from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.auth_service import role_required
from services.response_service import make_response
from services.optiongroup_service import create_application_group, get_application_groups, update_application_group, delete_application_group
from services.logger import loggie
from routes.admin.optiongroupitem import optiongroupitem_bp

optiongroup_bp = Blueprint("optiongroup", __name__)
optiongroup_bp.register_blueprint(optiongroupitem_bp, url_prefix="/<int:group_id>/item")


@optiongroup_bp.route('', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def create_group(application_id):
    """Create a new application option group."""
    data = request.get_json()
    result = create_application_group(application_id, data)
    return make_response(**result)

@optiongroup_bp.route('', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def fetch_groups(application_id):
    """Retrieve all application option groups."""
    result = get_application_groups(application_id)
    return make_response(**result)

@optiongroup_bp.route('<int:group_id>', methods=['PUT'])
@jwt_required()
@role_required(['admin'])
def modify_group(application_id, group_id):
    """Update an application option group."""
    data = request.get_json()
    result = update_application_group(application_id, group_id, data)
    return make_response(**result)

@optiongroup_bp.route('<int:group_id>', methods=['DELETE'])
@jwt_required()
@role_required(['admin'])
def remove_group(application_id, group_id):
    """Delete an application option group."""
    result = delete_application_group(application_id, group_id)
    return make_response(**result)