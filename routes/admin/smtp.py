from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.auth_service import role_required
from services.response_service import make_response
from services.smtp_service import create_smtp_server, get_smtp_servers, update_smtp_server, delete_smtp_server
from services.logger import loggie

smtp_bp = Blueprint("smtp", __name__, url_prefix="/smtp")

@smtp_bp.route('', methods=['POST'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def add_smtp_server():
    """Add a new SMTP server."""
    data = request.get_json()
    return make_response(**create_smtp_server(data))

@smtp_bp.route('', methods=['GET'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def list_smtp_servers():
    """Retrieve all SMTP servers."""
    return make_response(**get_smtp_servers())

@smtp_bp.route('/<int:smtp_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def edit_smtp_server(smtp_id):
    """Update an existing SMTP server."""
    data = request.get_json()
    return make_response(**update_smtp_server(smtp_id, data))

@smtp_bp.route('/<int:smtp_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def remove_smtp_server(smtp_id):
    """Delete an SMTP server."""
    return make_response(**delete_smtp_server(smtp_id))