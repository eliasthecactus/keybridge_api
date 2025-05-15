from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.auth_service import role_required
from services.response_service import make_response
from services.authsource_service import create_auth_source, get_auth_sources, get_auth_source, update_auth_source, delete_auth_source, test_auth_source_connection, search_auth_source
from services.logger import loggie
from models import db, AuthSource

authsource_bp = Blueprint("authsource", __name__)


@authsource_bp.route('/test', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def test_authsource():
    """Test LDAP authentication source."""
    data = request.get_json()
    return make_response(**test_auth_source_connection(data))

@authsource_bp.route('', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def add_auth_source():
    """Add a new authentication source."""
    data = request.get_json()
    return make_response(**create_auth_source(data))

@authsource_bp.route('', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def list_auth_sources():
    """Retrieve all authentication sources."""
    return make_response(**get_auth_sources())

@authsource_bp.route('/<int:auth_source_id>', methods=['PUT'])
@jwt_required()
@role_required(['admin'])
def edit_auth_source(auth_source_id):
    """Update authentication source."""
    data = request.get_json()
    return make_response(**update_auth_source(auth_source_id, data))

@authsource_bp.route('/<int:auth_source_id>', methods=['DELETE'])
@jwt_required()
@role_required(['admin'])
def remove_auth_source(auth_source_id):
    """Delete authentication source."""
    return make_response(**delete_auth_source(auth_source_id))

@authsource_bp.route('/search', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def search_ldap_endpoint():
    """
    Search for users or groups in the specified AuthSource (LDAP or RADIUS).
    """
    try:
        # Get required parameters
        auth_source_id = request.args.get('auth_source_id')

        if not auth_source_id:
            return make_response(code=30, message="AuthSource ID required", status_code=400)

        # Extract optional search parameters dynamically
        search_params = {key: request.args.get(key) for key in ["query", "uuid", "search_type", "username"] if request.args.get(key)}

        # Call the service function
        result = search_auth_source(auth_source_id, search_params)

        return make_response(**result)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return make_response(code=70, message="An unexpected error occurred", status_code=500)