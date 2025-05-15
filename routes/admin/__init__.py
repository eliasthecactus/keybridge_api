from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import role_required
from services.response_service import make_response
from routes.admin.license import license_bp
from routes.admin.auth import auth_bp
from routes.admin.authsource import authsource_bp
from routes.admin.syslog import syslog_bp
from routes.admin.smtp import smtp_bp
from routes.admin.application import application_bp
from routes.admin.logs import logs_bp
from routes.admin.access import access_bp
from routes.admin.mail import mail_bp
from routes.admin.objects import objects_bp
from routes.admin.twofa import twofa_bp
from routes.admin.setup import setup_bp

admin_bp = Blueprint("admin", __name__)

# Register all admin routes
admin_bp.register_blueprint(auth_bp, url_prefix="/auth")
admin_bp.register_blueprint(license_bp, url_prefix="/license")
admin_bp.register_blueprint(authsource_bp, url_prefix="/authsource")
admin_bp.register_blueprint(syslog_bp, url_prefix="/syslog")
admin_bp.register_blueprint(smtp_bp, url_prefix="/smtp")
admin_bp.register_blueprint(application_bp, url_prefix="/application")
admin_bp.register_blueprint(logs_bp, url_prefix="/logs")
admin_bp.register_blueprint(access_bp, url_prefix="/access")
admin_bp.register_blueprint(mail_bp, url_prefix="/mail")
admin_bp.register_blueprint(objects_bp, url_prefix="/objects")
admin_bp.register_blueprint(twofa_bp, url_prefix="/twofa")
admin_bp.register_blueprint(setup_bp, url_prefix="/setup")

