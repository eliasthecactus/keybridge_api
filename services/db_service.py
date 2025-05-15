import sys
import os
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.sql import text
from models import db, LocalUsers
from services.logger import loggie
from flask_migrate import upgrade, init, migrate, stamp

MIGRATIONS_PATH = "migrations"

def check_db_connection():
    """Check if the database connection is successful."""
    try:
        db.session.execute(text("SELECT 1"))
        loggie.info("Database connection successful.", do_db=False)
        return True
    except OperationalError as e:
        loggie.error(f"Database connection failed: {e}", do_db=False)
        return False
    except Exception as e:
        loggie.error(f"Unexpected error while checking DB: {e}", do_db=False)
        return False

# def check_db_schema():
#     """Ensure required tables exist, otherwise initialize/migrate."""
#     try:
#         if check_db_connection():
#             try:
#                 # Check if a critical table exists
#                 db.session.query(LocalUsers).first()
#                 loggie.info("Required tables exist in the database.")
#                 return True
#             except ProgrammingError:
#                 loggie.warning("Database schema is missing. Initializing...")
#                 return init_db()
#     except Exception as e:
#         loggie.error(f"Error while checking the database schema: {e}", do_db=False)
#         sys.exit(1)

# def init_db():
#     """Initialize and migrate the database schema if necessary."""
#     try:
#         if not os.path.exists(MIGRATIONS_PATH):
#             loggie.info("No migrations found. Initializing database...")
#             init(directory=MIGRATIONS_PATH)  # Initialize Flask-Migrate
#             stamp(directory=MIGRATIONS_PATH, revision="head")  # Mark as up-to-date
        
#         loggie.info("Running migrations...")
#         migrate(directory=MIGRATIONS_PATH, message="Initial migration")
#         upgrade(directory=MIGRATIONS_PATH)

#         loggie.info("Database successfully migrated and ready to use.")
#         return True
#     except Exception as e:
#         loggie.error(f"Failed to initialize/migrate database: {e}", do_db=False)
#         sys.exit(1)

# def ensure_db_integrity():
#     """Run all checks and apply migrations if necessary."""
#     loggie.info("Checking database integrity...")
#     if not check_db_schema():
#         loggie.error("Database integrity check failed. Exiting...")
#         sys.exit(1)
#     loggie.info("Database is properly configured and ready.")