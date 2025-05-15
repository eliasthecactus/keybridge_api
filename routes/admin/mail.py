from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services.auth_service import role_required
from services.response_service import make_response
from services.email_service import send_mail
from services.logger import loggie

mail_bp = Blueprint("mail", __name__)

@mail_bp.route("/", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def send_mail_endpoint():
    """
    Send an email to a specific address.
    ---
    Body JSON:
    {
        "to": "user@example.com",
        "caption": "Subject of the Email",
        "message": "Your email content"
    }
    """
    try:
        # Get data from request body
        data = request.get_json()
        to = data.get("to")
        message = data.get("message")
        caption = data.get("caption")

        # Validate input fields
        if not all([to, message, caption]):
            return make_response(code=30, message="Missing required fields", status_code=400)

        # Send email
        result = send_mail(to, message, caption)
        return make_response(**result)

    except Exception as e:
        loggie.error(f"Error sending email: {str(e)}")
        return make_response(code=70, message="An unexpected error occurred", status_code=500)