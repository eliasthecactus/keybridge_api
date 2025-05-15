from flask_jwt_extended import JWTManager
from services.response_service import make_response

def register_jwt_callbacks(jwt: JWTManager):
    """
    Registers JWT error handlers for invalid, expired, or missing tokens.
    """

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return make_response(
            code=401,
            message="Invalid or malformed token.",
            status_code=401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return make_response(
            code=401,
            message="Missing Authorization Header.",
            status_code=401
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return make_response(
            code=401,
            message="Your session has expired. Please log in again.",
            status_code=401
        )