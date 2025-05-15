from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import role_required, jwt_decoder
from services.response_service import make_response
from config import APIConfig

system_bp = Blueprint("system", __name__)

@system_bp.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint"""
    return make_response(code=0, message="pong", status_code=200)

@system_bp.route('/version', methods=['GET'])
def version_route():
    return make_response(code=0, message="API version retrieved", data={"version": APIConfig.API_VERSION}, status_code=200)

@system_bp.route('/authping', methods=['GET'])
@jwt_required()
@role_required(['client', 'admin', 'client_semi'])
def auth_ping():
    jwtecode = jwt_decoder(get_jwt_identity())
        
    # current_user_json = json.loads(current_user)
    return make_response(
        code=0,
        message="pong",
        # data={"user": jwtecode.get('user'), "role": jwtecode.get('type')},
        data={"details": jwtecode},
        status_code=200
    )