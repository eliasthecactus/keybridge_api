from models import db, SyslogServer
from services.logger import loggie
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError
from schemas import SyslogSchema

syslog_schema = SyslogSchema()
syslog_list_schema = SyslogSchema(many=True)

def create_syslog_server(data):
    """Create a new Syslog server."""
    try:
        # Validate data
        validated_data = syslog_schema.load(data)
        
        # Default protocol to UDP if not provided
        validated_data.setdefault("protocol", "udp")
        
        # Ensure protocol is either TCP or UDP
        if validated_data["protocol"] not in ["tcp", "udp"]:
            return {"code": 30, "message": "Invalid protocol. Allowed: 'tcp', 'udp'", "status_code": 400}
        
        # Create and save the new Syslog server
        new_syslog_server = SyslogServer(**validated_data)

        with db.session.begin_nested():
            db.session.add(new_syslog_server)
            db.session.commit()

        loggie.info(f"New Syslog server added: {validated_data['name']}")
        return {"code": 0, "message": "Syslog server added successfully", "status_code": 201}

    except ValidationError as e:
        return {"code": 40, "message": "Invalid request data", "data": e.messages, "status_code": 400}
    except IntegrityError:
        db.session.rollback()
        return {"code": 50, "message": "Syslog server with the same name already exists", "status_code": 409}
    except Exception as e:
        loggie.error(f"Unexpected error creating Syslog server: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def get_syslog_servers():
    """Retrieve all Syslog servers."""
    try:
        syslog_servers = SyslogServer.query.all()
        return {
            "code": 0,
            "message": "Syslog servers retrieved successfully",
            "data": syslog_list_schema.dump(syslog_servers),
            "status_code": 200,
        }
    except Exception as e:
        loggie.error(f"Unexpected error fetching Syslog servers: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def update_syslog_server(syslog_id, data):
    """Update a Syslog server."""
    try:
        syslog_server = db.session.get(SyslogServer, syslog_id)
        if not syslog_server:
            return {"code": 40, "message": "Syslog server not found", "status_code": 404}

        # Validate and update fields
        validated_data = syslog_schema.load(data, partial=True)
        for key, value in validated_data.items():
            setattr(syslog_server, key, value)

        db.session.commit()
        loggie.info(f"Syslog server updated: {syslog_server.name}")
        return {"code": 0, "message": "Syslog server updated successfully", "status_code": 200}

    except ValidationError as e:
        return {"code": 40, "message": "Invalid request data", "data": e.messages, "status_code": 400}
    except Exception as e:
        loggie.error(f"Unexpected error updating Syslog server: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def delete_syslog_server(syslog_id):
    """Delete a Syslog server."""
    try:
        syslog_server = db.session.get(SyslogServer, syslog_id)
        if not syslog_server:
            return {"code": 40, "message": "Syslog server not found", "status_code": 404}

        db.session.delete(syslog_server)
        db.session.commit()

        loggie.info(f"Syslog server deleted: {syslog_server.name}")
        return {"code": 0, "message": "Syslog server deleted successfully", "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error deleting Syslog server: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}