from sqlite3 import OperationalError
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, upgrade
import os
import sys
from dotenv import load_dotenv
from models import db
from config import APIConfig
from services.limiter import limiter
from services.logger import loggie
from services.db_service import check_db_connection
from routes import api_bp
from middlewares.error_handler import register_error_handlers
from middlewares.jwt_handler import register_jwt_callbacks
import time

load_dotenv()


app = Flask(__name__)
app.config.from_object(APIConfig)
app.url_map.strict_slashes = False

print(f"""
--- KeyBridge Configuration ---
API Version: {APIConfig.API_VERSION}
Database URI: {APIConfig.SQLALCHEMY_DATABASE_URI}
Debug Mode: {"Enabled" if APIConfig.DEBUG else "Disabled"}
API Port: {APIConfig.API_PORT}
--------------------------------
""")

script_path = os.path.dirname(os.path.realpath(__file__))


CORS(app)
db.init_app(app)
jwt = JWTManager(app)
register_jwt_callbacks(jwt)

migrate = Migrate(app, db)
# if APIConfig.DEBUG:
#     swagger = Swagger(app)
limiter.init_app(app)

with app.app_context():
    if not check_db_connection():
        loggie.info("Connection to DB failed. Exitig the application...", do_db=False)
        sys.exit(1)
    loggie.info("Starting KeyBridge API...", do_db=False)

    # Ensure tables are created if they do not exist
    loggie.info("Checking and creating missing tables...", do_db=False)
    db.create_all()  # Automatically creates missing tables
    # db.session.commit()


register_error_handlers(app)
app.register_blueprint(api_bp, url_prefix="/api")



@app.before_request
def log_request():
    return
    # loggie.info(f"Received request: {request.method} {request.url}")






if __name__ == '__main__':
    app.run(debug=APIConfig.DEBUG, port=APIConfig.API_PORT)

