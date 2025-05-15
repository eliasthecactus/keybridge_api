from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.auth_service import token_creator, role_required
from services.response_service import make_response
from services.logger import loggie
from services.object_service import get_all_objects
import json

objects_bp = Blueprint("objects", __name__)

@objects_bp.route("/", methods=["GET"])
@jwt_required()
@role_required(["admin"])
def get_users_endpoint():
    """Retrieve all Objects."""
    return make_response(**get_all_objects())
