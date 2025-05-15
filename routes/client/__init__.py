from flask import Blueprint
from routes.client.auth import client_auth_bp
from routes.client.application import client_application_bp
from routes.client.access import client_access_bp
from routes.client.launch import client_launch_bp

client_bp = Blueprint("client", __name__)

# Register all client routes
client_bp.register_blueprint(client_auth_bp, url_prefix="/auth")
client_bp.register_blueprint(client_application_bp, url_prefix="/applications")
client_bp.register_blueprint(client_access_bp, url_prefix="/access")
client_bp.register_blueprint(client_launch_bp, url_prefix="/launch")
