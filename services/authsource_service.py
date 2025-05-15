from models import db, AuthSource
from services.logger import loggie
import uuid
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError
from schemas import AuthSourceSchema
from services.ldap_service import connect_to_ldap, search_ldap

# Initialize schema
authsource_schema = AuthSourceSchema()
authsource_list_schema = AuthSourceSchema(many=True)

def create_auth_source(data):
    """Create a new authentication source."""
    try:
        # Validate request data
        validated_data = authsource_schema.load(data)
        new_auth_source = AuthSource(**validated_data)


        # Commit to the database
        with db.session.begin_nested():
            db.session.add(new_auth_source)
            db.session.commit()

        loggie.info(f"New authentication source added: {validated_data['name']}")
        return {"code": 0, "message": "Auth source added successfully", "status_code": 201}

    except ValidationError as e:
        return {"code": 40, "message": "Invalid request data", "data": e.messages, "status_code": 400}
    except IntegrityError as e:
        db.session.rollback()
        if "unique constraint" in str(e.orig):
            return {"code": 50, "message": "Auth source with the given name already exists", "status_code": 409}
        return {"code": 60, "message": f"Error adding auth source: {str(e)}", "status_code": 500}
    except Exception as e:
        loggie.error(f"Unexpected error creating auth source: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}


def get_auth_sources():
    """Retrieve all authentication sources."""
    try:
        auth_sources = AuthSource.query.all()
        return {
            "code": 0,
            "message": "Auth sources retrieved successfully",
            "data": authsource_list_schema.dump(auth_sources),
            "status_code": 200,
        }
    except Exception as e:
        loggie.error(f"Unexpected error fetching auth sources: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}


def get_auth_source(auth_source_id):
    """Retrieve a single authentication source."""
    auth_source = db.session.get(AuthSource, auth_source_id)
    if not auth_source:
        return {"code": 40, "message": "Auth source not found", "status_code": 404}

    return {
        "code": 0,
        "message": "Auth source retrieved successfully",
        "data": authsource_schema.dump(auth_source),
        "status_code": 200,
    }


def update_auth_source(auth_source_id, data):
    """Update an existing authentication source."""
    try:
        auth_source = db.session.get(AuthSource, auth_source_id)
        if not auth_source:
            return {"code": 40, "message": "Auth source not found", "status_code": 404}

        validated_data = authsource_schema.load(data, partial=True)

        for key, value in validated_data.items():
            setattr(auth_source, key, value)

        db.session.commit()
        loggie.info(f"Auth source updated: {auth_source.name}")
        return {"code": 0, "message": "Auth source updated successfully", "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error updating auth source: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}


def delete_auth_source(auth_source_id):
    """Delete an authentication source."""
    try:
        auth_source = db.session.get(AuthSource, auth_source_id)
        if not auth_source:
            return {"code": 40, "message": "Auth source not found", "status_code": 404}

        db.session.delete(auth_source)
        db.session.commit()

        loggie.info(f"Auth source deleted: {auth_source.name}")
        return {"code": 0, "message": "Auth source deleted successfully", "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error deleting auth source: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}


def test_auth_source_connection(data):
    """Test LDAP connection with given or stored credentials."""
    try:
        auth_source_id = data.get("manualID")

        if auth_source_id:
            auth_source = db.session.get(AuthSource, auth_source_id)
            if not auth_source:
                return {"code": 40, "message": "Auth source not found", "status_code": 404}
            
            # Extract stored credentials
            ssl = auth_source.ssl
            host = auth_source.host
            port = auth_source.port
            bind_password = auth_source.bind_password
            bind_user_dn = auth_source.bind_user_dn
        else:
            # Use provided credentials
            ssl = data.get("ssl", False)
            host = data.get("host")
            port = data.get("port")
            bind_password = data.get("bind_password")
            bind_user_dn = data.get("bind_user_dn")

        if not host or not port or not bind_password or not bind_user_dn:
            return {"code": 30, "message": "Missing required fields", "status_code": 400}

        server = connect_to_ldap(host, bind_user_dn, bind_password, port=port, ssl=ssl)

        if not server.bind():
            return {"code": 50, "message": f"Error binding to LDAP server: {server.result}", "status_code": 500}

        return {"code": 0, "message": "Bind successful", "status_code": 200}

    except Exception as e:
        loggie.error(f"Error connecting to LDAP server: {str(e)}")
        return {"code": 50, "message": "Unknown error while binding to LDAP server", "status_code": 500}
    

def search_auth_source(auth_source_id, search_params):
    """Search for users or groups in a given AuthSource (LDAP or RADIUS)."""

    try:
        # Convert `auth_source_id` to an integer
        try:
            auth_source_id = int(auth_source_id)
        except ValueError:
            return {"code": 31, "message": "AuthSource ID must be an integer", "status_code": 400}

        # Fetch the AuthSource from the database
        auth_source = db.session.get(AuthSource, auth_source_id)
        if not auth_source:
            return {"code": 40, "message": "AuthSource not found", "status_code": 404}

        # Connect to the LDAP server
        server = connect_to_ldap(
            auth_source.host,
            bind_dn=auth_source.bind_user_dn,
            password=auth_source.bind_password,
            port=auth_source.port,
            ssl=auth_source.ssl
        )
        
        if not server.bind():
            return {"code": 50, "message": "Error binding to the LDAP server", "status_code": 500}

        # Perform the LDAP search
        results = search_ldap(
            server,
            base_dn=auth_source.base_dn,
            is_ad=(auth_source.server_type == "ad"),
            **search_params  # Pass all additional query parameters dynamically
        )

        return {"code": 0, "message": "Search results retrieved successfully", "status_code": 200, "data": results}

    except SQLAlchemyError as e:
        loggie.error(f"Database error: {str(e)}")
        return {"code": 50, "message": "Database error occurred", "status_code": 500}
    except Exception as e:
        loggie.error(f"Unexpected error during AuthSource search: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}