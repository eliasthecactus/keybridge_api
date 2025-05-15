from flask import jsonify
from services.response_service import make_response
from services.logger import loggie

def register_error_handlers(app):
    """Registers global error handlers."""

    @app.errorhandler(Exception)
    def generic_error_handler(error):
        """Handles unexpected server errors."""
        loggie.error(f"Unexpected error: {error}")
        return make_response(
            code=500,
            message="An unexpected error occurred. Please try again later.",
            status_code=500
        )

    @app.errorhandler(404)
    def page_not_found(error):
        """Handles 404 errors (not found)."""
        return make_response(
            code=404,
            message="The requested resource was not found.",
            status_code=404
        )

    @app.errorhandler(429)
    def too_many_requests(error):
        """Handles rate limit errors."""
        return make_response(
            code=429,
            message="Too many requests. Please try again later.",
            status_code=429
        )

    @app.errorhandler(401)
    def unauthorized(error):
        """Handles unauthorized errors."""
        return make_response(
            code=401,
            message="Unauthorized access.",
            status_code=401
        )

    @app.errorhandler(403)
    def forbidden(error):
        """Handles forbidden access errors."""
        return make_response(
            code=403,
            message="Forbidden: You do not have permission to access this resource.",
            status_code=403
        )