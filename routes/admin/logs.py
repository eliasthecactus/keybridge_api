from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.auth_service import role_required
from services.log_service import get_logs_service
from services.response_service import make_response

logs_bp = Blueprint("logs", __name__)

@logs_bp.route("/", methods=["GET"])
@jwt_required()
@role_required(["admin"])
def get_logs():
    """Retrieve logs with filtering, sorting, and pagination."""
    result = get_logs_service(request.args)
    return make_response(**result)