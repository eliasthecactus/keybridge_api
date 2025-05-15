from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import role_required
from services.response_service import make_response
from routes.system import system_bp
from routes.admin import admin_bp
from routes.client import client_bp

api_bp = Blueprint("api", __name__)

# Register all admin routes
api_bp.register_blueprint(system_bp)
api_bp.register_blueprint(admin_bp, url_prefix="/admin")
api_bp.register_blueprint(client_bp, url_prefix="/client")

