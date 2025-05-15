from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.auth_service import role_required
from services.response_service import make_response
from services.syslog_service import create_syslog_server, get_syslog_servers, update_syslog_server, delete_syslog_server
from services.logger import loggie

syslog_bp = Blueprint("syslog", __name__)

@syslog_bp.route('', methods=['POST'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def add_syslog_server():
    """Add a new Syslog server."""
    data = request.get_json()
    return make_response(**create_syslog_server(data))

@syslog_bp.route('', methods=['GET'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def list_syslog_servers():
    """Retrieve all Syslog servers."""
    return make_response(**get_syslog_servers())

@syslog_bp.route('/<int:syslog_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def edit_syslog_server(syslog_id):
    """Update an existing Syslog server."""
    data = request.get_json()
    return make_response(**update_syslog_server(syslog_id, data))

@syslog_bp.route('/<int:syslog_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@role_required(['admin'])
def remove_syslog_server(syslog_id):
    """Delete a Syslog server."""
    return make_response(**delete_syslog_server(syslog_id))