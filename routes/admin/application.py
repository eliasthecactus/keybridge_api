from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.auth_service import role_required
from services.response_service import make_response
from services.application_service import create_application,get_applications,update_application,delete_application,add_application_image, remove_application_image
from services.logger import loggie
from routes.admin.optiongroup import optiongroup_bp

application_bp = Blueprint("application", __name__)
application_bp.register_blueprint(optiongroup_bp, url_prefix="/<int:application_id>/optiongroup")


# Add an application
@application_bp.route('', methods=['POST'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def add_application():
    """Add a new application"""
    data = request.get_json()
    return make_response(**create_application(data))

# Get all applications or a single application by ID
@application_bp.route('', methods=['GET'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def list_applications():
    """Retrieve applications"""
    application_id = request.args.get("id", type=int)
    return make_response(**get_applications(application_id))

# Update an application
@application_bp.route('/<int:application_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def modify_application(application_id):
    """Modify an existing application"""
    data = request.get_json()
    return make_response(**update_application(application_id, data))

# Delete an application
@application_bp.route('/<int:application_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def remove_application(application_id):
    """Delete an application"""
    return make_response(**delete_application(application_id))

# Add an application image
@application_bp.route('/<int:application_id>/image', methods=['POST'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def upload_application_image(application_id):
    """Upload an application image"""
    return make_response(**add_application_image(application_id, request.files))

# Remove an application image
@application_bp.route('/<int:application_id>/image', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def delete_application_image(application_id):
    """Remove an application image"""
    return make_response(**remove_application_image(application_id))