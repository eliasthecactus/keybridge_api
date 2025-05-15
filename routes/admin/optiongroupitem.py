from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.auth_service import role_required
from services.response_service import make_response
from services.optiongroupitem_service import add_application_group_item,get_application_group_items,update_application_group_item,delete_application_group_item
from services.logger import loggie

optiongroupitem_bp = Blueprint("optiongroupitem", __name__)

@optiongroupitem_bp.route("/", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def create_item(application_id, group_id):
    """Create a new item in an application option group."""
    data = request.get_json()
    result = add_application_group_item(application_id, group_id, data)
    return make_response(**result)

@optiongroupitem_bp.route("/", methods=["GET"])
@jwt_required()
@role_required(["admin"])
def fetch_items(application_id, group_id):
    """Retrieve all items from an application option group."""
    result = get_application_group_items(application_id, group_id)
    return make_response(**result)

@optiongroupitem_bp.route("/<int:item_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin"])
def modify_item(application_id, group_id, item_id):
    """Update an item in an application option group."""
    data = request.get_json()
    result = update_application_group_item(application_id, group_id, item_id, data)
    return make_response(**result)

@optiongroupitem_bp.route("/<int:item_id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def remove_item(application_id, group_id, item_id):
    """Delete an item from an application option group."""
    result = delete_application_group_item(application_id, group_id, item_id)
    return make_response(**result)